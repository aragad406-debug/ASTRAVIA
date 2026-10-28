from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.characters.models import Character, CharacterRelationship
from apps.core.conditions import ConditionContext, evaluate, validate_condition
from apps.core.models import ContentStatus, Visibility
from apps.core.text import normalize_search_text
from apps.dialogues.models import DialogueChoice, DialogueEntry
from apps.dialogues.services import guide_lines, primary_guide
from apps.narrative.graph import validate_chapter
from apps.narrative.models import StoryArc, StoryBranch, StoryChapter, StoryNode
from apps.quests.models import Quest, QuestDependency, QuestObjective, QuestState
from apps.quests.services import complete_quest, quest_status_for, start_quest
from apps.worlds.models import World

from .helpers import make_user, seed


class SeedTests(TestCase):
    def test_seed_is_idempotent_and_preserves_edits(self):
        seed()
        counts = (World.objects.count(), Character.objects.count(), DialogueEntry.objects.count())
        world = World.objects.get(slug="everfrost")
        world.tagline_en = "Edited by the owner"
        world.revision = 2
        world.save()
        seed()
        self.assertEqual(counts, (World.objects.count(), Character.objects.count(), DialogueEntry.objects.count()))
        self.assertEqual(World.objects.get(slug="everfrost").tagline_en, "Edited by the owner")

    def test_canon(self):
        seed()
        self.assertEqual(World.objects.public().count(), 5)
        self.assertEqual(World.objects.get(slug="umbra").visibility, Visibility.HIDDEN)
        zerath = Character.objects.get(slug="zerath")
        self.assertEqual((zerath.age_years, zerath.transformation_age), (1247, 30))
        self.assertTrue(CharacterRelationship.objects.filter(from_character=zerath, to_character__slug="eilen", kind="parent_of").exists())
        # Noxar's sister is a separate identity from Eilen.
        sister = CharacterRelationship.objects.get(from_character__slug="noxar", kind="sibling").to_character
        self.assertNotEqual(sister.slug, "eilen")
        closing = StoryChapter.objects.get(slug="spring-in-the-garden").closing_line_ar
        self.assertEqual(closing, "بعض الوعود لا تتحقق في هذه الحياة... لكنها تجد طريقها إلى النجوم.")


class WorldTests(TestCase):
    def setUp(self):
        seed()

    def test_create_edit_and_unique_slug(self):
        w = World.objects.create(slug="new-world", name_en="New", status=ContentStatus.DRAFT)
        w.name_ar = "جديد"
        w.save()
        self.assertEqual(World.objects.get(slug="new-world").name_ar, "جديد")
        with self.assertRaises(IntegrityError), transaction.atomic():
            World.objects.create(slug="new-world", name_en="Duplicate")

    def test_colour_validation(self):
        w = World(slug="bad", name_en="Bad", color_primary="red;}body{")
        with self.assertRaises(ValidationError):
            w.full_clean()

    def test_published_visibility_on_public_pages(self):
        World.objects.create(slug="draft-world", name_en="Draft world", status=ContentStatus.DRAFT)
        self.assertEqual(self.client.get(reverse("worlds:detail", args=["everfrost"])).status_code, 200)
        self.assertEqual(self.client.get(reverse("worlds:detail", args=["draft-world"])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("worlds:list")), "Draft world")

    def test_hidden_world_restrictions(self):
        self.assertEqual(self.client.get("/worlds/umbra/").status_code, 404)
        home = self.client.get("/")
        self.assertNotContains(home, "Umbra")
        self.assertNotContains(self.client.get("/sitemap.xml"), "umbra")
        self.assertEqual(self.client.get("/search/?q=umbra").context["result_count"], 0)
        insider = make_user("lore@example.com", "Narrative Editor")
        self.client.force_login(insider)
        self.assertEqual(self.client.get("/worlds/umbra/").status_code, 200)

    def test_teaser_world_hides_details(self):
        World.objects.filter(slug="umbra").update(visibility=Visibility.TEASER)
        r = self.client.get("/worlds/umbra/")
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Empty Palace")

    def test_scheduled_content_goes_live_at_time(self):
        w = World.objects.create(slug="soon", name_en="Soon", status=ContentStatus.SCHEDULED,
                                 publish_at=timezone.now() + timezone.timedelta(hours=1))
        self.assertFalse(World.objects.published().filter(pk=w.pk).exists())
        World.objects.filter(pk=w.pk).update(publish_at=timezone.now() - timezone.timedelta(minutes=1))
        self.assertTrue(World.objects.published().filter(pk=w.pk).exists())


class CharacterTests(TestCase):
    def setUp(self):
        seed()

    def test_character_world_and_localization(self):
        c = Character.objects.get(slug="kaizen")
        self.assertEqual(c.world.slug, "solaris")
        self.assertEqual(c.loc("name", "ar"), "كايزن")
        self.assertEqual(c.loc("name", "en"), "Kaizen")
        c.title_ar = ""
        self.assertEqual(c.loc("title", "ar"), "The Desert Emperor")  # English fallback
        self.assertIn(("title", "ar"), c.missing_translations())

    def test_relationship_validation(self):
        z = Character.objects.get(slug="zerath")
        e = Character.objects.get(slug="eilen")
        with self.assertRaises(ValidationError):
            CharacterRelationship(from_character=z, to_character=z, kind="ally").full_clean()
        with self.assertRaises(ValidationError):
            CharacterRelationship(from_character=e, to_character=z, kind="parent_of").full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            CharacterRelationship.objects.create(from_character=z, to_character=z, kind="ally")

    def test_secrets_never_public(self):
        r = self.client.get("/characters/zerath/")
        self.assertNotContains(r, "Hollow King gave him the crown")
        r = self.client.get("/api/v1/characters/zerath/")
        self.assertNotIn("secrets", r.json())
        self.assertNotIn("Hollow King gave him", r.content.decode())


class StoryTests(TestCase):
    def setUp(self):
        seed()
        self.arc = StoryArc.objects.create(slug="test-arc", title_en="Test arc", status=ContentStatus.PUBLISHED)
        self.chapter = StoryChapter.objects.create(arc=self.arc, slug="one", order=1, title_en="One", status=ContentStatus.PUBLISHED)

    def test_chapter_ordering_and_navigation(self):
        two = StoryChapter.objects.create(arc=self.arc, slug="two", order=2, title_en="Two", status=ContentStatus.PUBLISHED)
        self.assertEqual(self.chapter.next_chapter(), two)
        self.assertEqual(two.previous_chapter(), self.chapter)
        with self.assertRaises(IntegrityError), transaction.atomic():
            StoryChapter.objects.create(arc=self.arc, slug="dup", order=2, title_en="Dup")

    def test_valid_graph(self):
        self.assertEqual(validate_chapter(StoryChapter.objects.get(slug="the-crowns-grip"))["errors"], [])

    def test_invalid_graph_detected(self):
        a = StoryNode.objects.create(chapter=self.chapter, key="a", is_start=True)
        b = StoryNode.objects.create(chapter=self.chapter, key="b")
        StoryNode.objects.create(chapter=self.chapter, key="orphan", node_type="ending", ending_type="canonical")
        StoryBranch.objects.create(from_node=a, to_node=b)
        errors = validate_chapter(self.chapter)["errors"]
        self.assertTrue(any("dead end" in e for e in errors))
        self.assertTrue(any("never be reached" in e for e in errors))

    def test_invalid_branch_rejected(self):
        a = StoryNode.objects.create(chapter=self.chapter, key="a", is_start=True)
        other_arc_node = StoryNode.objects.filter(chapter__slug="the-crowns-grip").first()
        with self.assertRaises(ValidationError):
            StoryBranch(from_node=a, to_node=other_arc_node).full_clean()
        with self.assertRaises(ValidationError):
            StoryBranch(from_node=a, to_node=a).full_clean()
        b = StoryNode.objects.create(chapter=self.chapter, key="b")
        with self.assertRaises(ValidationError):
            StoryBranch(from_node=a, to_node=b, condition={"lore": "does-not-exist"}).full_clean()
        with self.assertRaises(ValidationError):
            StoryBranch(from_node=a, to_node=b, consequences=[{"exec": "rm -rf"}]).full_clean()

    def test_two_start_nodes_rejected(self):
        StoryNode.objects.create(chapter=self.chapter, key="s1", is_start=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            StoryNode.objects.create(chapter=self.chapter, key="s2", is_start=True)

    def test_draft_chapter_hidden_then_published(self):
        StoryChapter.objects.create(arc=self.arc, slug="draft", order=3, title_en="Secret draft")
        self.assertEqual(self.client.get("/story/test-arc/draft/").status_code, 404)
        self.assertNotContains(self.client.get("/story/test-arc/"), "Secret draft")
        StoryChapter.objects.filter(slug="draft").update(status=ContentStatus.PUBLISHED)
        self.assertEqual(self.client.get("/story/test-arc/draft/").status_code, 200)


class ConditionTests(TestCase):
    def test_grammar_validation(self):
        self.assertEqual(validate_condition({}), [])
        self.assertEqual(validate_condition({"all": [{"quest": "a", "state": "completed"}, {"not": {"flag": "x"}}]}), [])
        self.assertTrue(validate_condition({"eval": "__import__('os')"}))
        self.assertTrue(validate_condition({"quest": "a", "state": "dancing"}))
        self.assertTrue(validate_condition({"all": []}))
        deep = {"not": {}}
        for _ in range(12):
            deep = {"not": deep}
        self.assertTrue(validate_condition(deep))

    def test_evaluation(self):
        ctx = ConditionContext(quest_states={"a": "completed"}, discovered_lore={"l"}, flags={"x": True})
        self.assertTrue(evaluate({"all": [{"quest": "a"}, {"lore": "l"}, {"flag": "x", "equals": True}]}, ctx))
        self.assertFalse(evaluate({"any": [{"quest": "b"}, {"not": {"lore": "l"}}]}, ctx))
        self.assertFalse(evaluate({"unknown": 1}, ctx))

    def test_arabic_normalization(self):
        self.assertEqual(normalize_search_text("أَسْتْرَافِيَا"), normalize_search_text("استرافيا"))
        self.assertEqual(normalize_search_text("مدينة"), normalize_search_text("مدينه"))


class DialogueTests(TestCase):
    def setUp(self):
        seed()

    def test_choices_and_language(self):
        entry = DialogueEntry.objects.get(key="zerath-boss-intro")
        self.assertEqual(entry.choices.count(), 2)
        self.assertEqual(entry.choices.first().next_entry.key, "zerath-why")
        self.assertEqual(entry.loc("text", "ar"), entry.text_ar)

    def test_invalid_references(self):
        entry = DialogueEntry.objects.get(key="zerath-boss-intro")
        with self.assertRaises(ValidationError):
            DialogueChoice(entry=entry, text_en="Loop", next_entry=entry).full_clean()
        with self.assertRaises(ValidationError):
            DialogueEntry(key="empty-line").full_clean()
        with self.assertRaises(ValidationError):
            DialogueEntry(key="bad-cond", text_en="x", conditions={"quest": "missing-quest"}).full_clean()

    def test_guide_trigger_conditions(self):
        guide = primary_guide()
        home = [l.key for l in guide_lines(guide, page="home")]
        self.assertEqual(home[0], "guide-home-greeting")
        world = [l.key for l in guide_lines(guide, page="world", world_slug="everfrost")]
        self.assertEqual(world[0], "guide-world-everfrost")
        self.assertNotIn("guide-world-solaris", world)
        line = DialogueEntry.objects.get(key="guide-home-sixth")
        line.conditions = {"flag": "saw_sixth_orbit"}
        line.save()
        self.assertNotIn("guide-home-sixth", [l.key for l in guide_lines(guide, page="home")])


class QuestTests(TestCase):
    def setUp(self):
        seed()
        self.player = make_user("quest@example.com")

    def test_prerequisites_and_completion(self):
        first = Quest.objects.get(slug="the-silent-festival")
        second = Quest.objects.get(slug="letters-to-a-daughter")
        self.assertEqual(quest_status_for(self.player, second), QuestState.LOCKED)
        with self.assertRaises(ValidationError):
            start_quest(self.player, second)
        record = start_quest(self.player, first)
        with self.assertRaises(ValidationError):  # objectives unfinished
            complete_quest(self.player, first)
        record.objective_progress = {"reach-square": 1, "unfinished-letter": 1}
        record.save()
        complete_quest(self.player, first)
        self.assertEqual(quest_status_for(self.player, second), QuestState.AVAILABLE)

    def test_completion_conditions(self):
        boss = Quest.objects.get(slug="shatter-the-crown")
        QuestDependency.objects.filter(quest=boss).delete()
        rec = start_quest(self.player, boss)
        rec.objective_progress = {"confront-zerath": 1}
        rec.save()
        with self.assertRaises(ValidationError):
            complete_quest(self.player, boss)
        complete_quest(self.player, boss, {"flags": {"crown_broken": True}})

    def test_objective_and_dependency_validation(self):
        q = Quest.objects.get(slug="the-silent-festival")
        with self.assertRaises(ValidationError):
            QuestObjective(quest=q, key="x", description_en="x", required_count=0).full_clean()
        later = Quest.objects.get(slug="spring-returns")
        with self.assertRaises(ValidationError):  # would create a cycle
            QuestDependency(quest=q, requires=later).full_clean()

    def test_publication_restrictions(self):
        Quest.objects.filter(slug="spring-returns").update(status=ContentStatus.DRAFT)
        self.assertEqual(self.client.get("/quests/spring-returns/").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/quests/spring-returns/").status_code, 404)
        with self.assertRaises(ValidationError):
            start_quest(self.player, Quest.objects.get(slug="spring-returns"))
