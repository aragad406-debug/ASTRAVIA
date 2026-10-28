"""Create ASTRAVIA's canonical starting universe.

Safe to rerun: records are matched by stable slugs/keys and only created when missing.
Edited content is never overwritten. `--refresh` updates only records that are still marked as seeded
and have never been revised in the Creator Studio (revision == 1).
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.announcements.models import Announcement
from apps.characters.models import Character, CharacterRelationship
from apps.core import seed_data as D
from apps.core.models import ContentStatus, Page, SiteConfiguration
from apps.dialogues.models import DialogueChoice, DialogueEntry, GuideAssistant, VoiceProfile
from apps.localization.models import GlossaryTerm
from apps.narrative.models import Artifact, Cinematic, CinematicScene, LoreEntry, StoryArc, StoryBranch, StoryChapter, StoryNode
from apps.quests.models import BossEncounter, BossPhase, Quest, QuestDependency, QuestObjective, QuestReward
from apps.worlds.models import Region, World

PUBLISHED = ContentStatus.PUBLISHED


class Command(BaseCommand):
    help = "Seed the canonical ASTRAVIA worlds, characters, story, quests, dialogue and lore (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--refresh", action="store_true", help="Update seeded records that were never edited.")

    def handle(self, *args, **opts):
        self.refresh = opts["refresh"]
        self.created = 0
        self.updated = 0
        with transaction.atomic():
            self.seed()
        if opts.get("verbosity", 1):
            self.stdout.write(self.style.SUCCESS(f"ASTRAVIA seed complete: {self.created} created, {self.updated} refreshed."))

    # ----------------------------------------------------------------- helpers
    def upsert(self, model, lookup, defaults, publishable=True):
        if publishable:
            defaults = {"status": PUBLISHED, "is_seeded": True, **defaults}
            if defaults["status"] == PUBLISHED:
                defaults.setdefault("published_at", timezone.now())
        obj = model.objects.filter(**lookup).first()
        if obj is None:
            obj = model(**lookup, **defaults)
            obj.save()
            self.created += 1
            return obj, True
        if self.refresh and getattr(obj, "is_seeded", False) and getattr(obj, "revision", 1) <= 1:
            for key, value in defaults.items():
                if key != "published_at":
                    setattr(obj, key, value)
            obj.save()
            self.updated += 1
        return obj, False

    def seed(self):
        site = SiteConfiguration.load()
        if not site.hero_intro_en:
            for key, value in D.SITE.items():
                setattr(site, key, value)
            site.save()

        worlds = {}
        for w in D.WORLDS:
            obj, _ = self.upsert(World, {"slug": w["slug"]}, {
                "order": w["order"], "theme": w["theme"], "visibility": w.get("visibility", "public"),
                "color_primary": w["colors"][0], "color_secondary": w["colors"][1], "color_accent": w["colors"][2],
                **{k: w[k] for k in w if k.endswith(("_en", "_ar"))},
            })
            worlds[w["slug"]] = obj
            for order, (slug, en, ar, kind, den, dar) in enumerate(w["regions"], start=1):
                if not Region.objects.filter(world=obj, slug=slug).exists():
                    Region.objects.create(world=obj, slug=slug, name_en=en, name_ar=ar, kind=kind, order=order,
                                          description_en=den, description_ar=dar, is_secret=kind == "hidden")
                    self.created += 1

        chars = {}
        for c in D.CHARACTERS:
            obj, _ = self.upsert(Character, {"slug": c["slug"]}, {
                "category": c["category"], "world": worlds.get(c["world"]) if c["world"] else None, "order": c["order"],
                "signature_color": c["color"], "age_years": c.get("age"), "age_is_unknown": c.get("age_unknown", False),
                "transformation_age": c.get("transformation_age"), "visibility": c.get("visibility", "public"),
                **{k: c[k] for k in c if k.endswith(("_en", "_ar"))},
            })
            chars[c["slug"]] = obj
        for w in D.WORLDS:
            world = worlds[w["slug"]]
            if world.ruler_id is None and w.get("ruler") in chars:
                world.ruler = chars[w["ruler"]]
                world.save(update_fields=["ruler", "updated_at"])

        for src, dst, kind, den, dar, secret in D.RELATIONSHIPS:
            if src in chars and dst in chars and kind:
                _, made = CharacterRelationship.objects.get_or_create(
                    from_character=chars[src], to_character=chars[dst], kind=kind,
                    defaults={"description_en": den, "description_ar": dar, "is_secret": secret},
                )
                self.created += int(made)

        artifacts = {}
        for slug, en, ar, world, rarity, key_item, den, dar in D.ARTIFACTS:
            obj, made = Artifact.objects.get_or_create(slug=slug, defaults={
                "name_en": en, "name_ar": ar, "world": worlds.get(world), "rarity": rarity, "is_key_item": key_item,
                "description_en": den, "description_ar": dar,
            })
            artifacts[slug] = obj
            self.created += int(made)

        lore = {}
        for entry in D.LORE:
            obj, made = self.upsert(LoreEntry, {"slug": entry["slug"]}, {
                "entry_type": entry["type"], "importance": entry["importance"], "timeline_position": entry["timeline"],
                "visibility": entry.get("visibility", "public"),
                **{k: entry[k] for k in entry if k.endswith(("_en", "_ar"))},
            })
            lore[entry["slug"]] = obj
            if made:
                obj.worlds.set([worlds[s] for s in entry.get("worlds", [])])
                obj.characters.set([chars[s] for s in entry.get("characters", [])])
        for entry in D.LORE:  # cross references once every entry exists
            if entry.get("related"):
                lore[entry["slug"]].related_entries.add(*[lore[s] for s in entry["related"] if s in lore])

        quests = {}
        for q in D.QUESTS:
            obj, made = self.upsert(Quest, {"slug": q["slug"]}, {
                "quest_type": q["type"], "world": worlds.get(q["world"]), "order": q["order"],
                "giver": chars.get(q["giver"]) if q.get("giver") else None, "visibility": q.get("visibility", "public"),
                "title_en": q["title_en"], "title_ar": q["title_ar"],
                "summary_en": q["summary_en"], "summary_ar": q["summary_ar"],
            })
            quests[q["slug"]] = obj
            if made:
                for order, (key, otype, den, dar, count, optional) in enumerate(q["objectives"], start=1):
                    QuestObjective.objects.create(quest=obj, key=key, order=order, objective_type=otype,
                                                  description_en=den, description_ar=dar, required_count=count, is_optional=optional)
                for rtype, artifact, lore_slug, den, dar in q["rewards"]:
                    QuestReward.objects.create(quest=obj, reward_type=rtype, artifact=artifacts.get(artifact),
                                               lore=lore.get(lore_slug), description_en=den, description_ar=dar)
                    if lore_slug:
                        obj.unlocks_lore.add(lore[lore_slug])
                        lore[lore_slug].quests.add(obj)
        for q in D.QUESTS:  # dependencies and conditions once all quests exist
            obj = quests[q["slug"]]
            for req in q.get("requires", []):
                QuestDependency.objects.get_or_create(quest=obj, requires=quests[req])
            changed = False
            if q.get("start") and not obj.start_conditions:
                obj.start_conditions, changed = q["start"], True
            if q.get("completion") and not obj.completion_conditions:
                obj.completion_conditions, changed = q["completion"], True
            if changed:
                obj.save(update_fields=["start_conditions", "completion_conditions", "updated_at"])
        # Discovery condition references a quest, so set it after quests exist.
        for entry in D.LORE:
            if entry.get("discovery") and not lore[entry["slug"]].discovery_conditions:
                lore[entry["slug"]].discovery_conditions = entry["discovery"]
                lore[entry["slug"]].save(update_fields=["discovery_conditions", "updated_at"])

        dialogue = {}
        guide_char = chars["celestial-guide"]
        guide, made = GuideAssistant.objects.get_or_create(slug="celestial-guide", defaults={
            "character": guide_char, "is_primary": True, "status": PUBLISHED, "published_at": timezone.now(),
            "is_seeded": True, "supported_languages": ["en", "ar"], "trigger_pages": [],
            "purpose_en": "Guides visitors and players through the five worlds, introduces each world, explains discovered "
            "lore and offers hints without spoiling turning points.",
            "purpose_ar": "ترشد الزوّار واللاعبين عبر العوالم الخمسة، وتعرّف بكل عالم، وتشرح السجلات المكتشفة، وتقدّم التلميحات دون "
            "إفساد نقاط التحوّل.",
            "intro_narration_en": "I have walked every world in ASTRAVIA. Ask, and I will tell you what I can.",
            "intro_narration_ar": "سرتُ في كل عوالم أسترافيا. اسأل، وسأخبرك بما أستطيع.",
            "voice_description_en": "Low, warm and unhurried, with a faint smile behind serious words.",
            "voice_description_ar": "صوتٌ هادئ دافئ متأنٍّ، تلوح خلف كلماته الجادّة ابتسامةٌ خفيفة.",
        })
        self.created += int(made)
        if made:
            guide.related_worlds.set([worlds[s] for s in ("everfrost", "verdant-realm", "solaris", "nyxara", "astrion")])
        for lang in ("en", "ar"):
            vp, made = VoiceProfile.objects.get_or_create(slug=f"celestial-guide-{lang}", defaults={
                "character": guide_char, "name": f"Celestial Guide ({'Arabic' if lang == 'ar' else 'English'})",
                "language": lang, "provider": VoiceProfile.Provider.MANUAL,
                "description": "Low, warm, unhurried. Formal Modern Standard Arabic delivery." if lang == "ar" else "Low, warm, unhurried.",
                "pronunciation_notes": "Astravia: as-TRAH-vee-ah." if lang == "en" else "أسترافيا: بفتح الهمزة.",
            })
            self.created += int(made)
            if made and lang == "en" and guide.voice_profile_id is None:
                guide.voice_profile = vp
                guide.save(update_fields=["voice_profile"])

        for d in D.DIALOGUE:
            obj, _ = self.upsert(DialogueEntry, {"key": d["key"]}, {
                "status": d.get("status", PUBLISHED), "guide": guide if d.get("guide") else None,
                "speaker": guide_char if d.get("guide") else chars.get(d.get("speaker")),
                "category": d["category"], "page_context": d.get("page", "any"), "priority": d.get("priority", 0),
                "emotion": d.get("emotion", "neutral"), "world": worlds.get(d.get("world")), "quest": quests.get(d.get("quest")),
                "trigger_event": d.get("trigger", ""), "text_en": d["en"], "text_ar": d["ar"],
            })
            dialogue[d["key"]] = obj
        for d in D.DIALOGUE:
            entry = dialogue[d["key"]]
            if d.get("choices") and not entry.choices.exists():
                for order, (en, ar, nxt) in enumerate(d["choices"], start=1):
                    DialogueChoice.objects.create(entry=entry, order=order, text_en=en, text_ar=ar, next_entry=dialogue.get(nxt))

        chapters = {}
        for arc_data in D.ARCS:
            arc, made = self.upsert(StoryArc, {"slug": arc_data["slug"]}, {
                "arc_type": arc_data["arc_type"], "order": arc_data["order"], "world": worlds.get(arc_data["world"]),
                "visibility": arc_data.get("visibility", "public"),
                **{k: arc_data[k] for k in arc_data if k.endswith(("_en", "_ar"))},
            })
            if made:
                arc.characters.set([chars[s] for s in arc_data.get("characters", [])])
            for ch in arc_data["chapters"]:
                chapter, made = self.upsert(StoryChapter, {"arc": arc, "slug": ch["slug"]}, {
                    "order": ch["order"], "chapter_type": ch["type"], "world": arc.world, "is_spoiler": ch.get("spoiler", False),
                    "ending_type": ch.get("ending", ""),
                    **{k: ch[k] for k in ch if k.endswith(("_en", "_ar"))},
                })
                chapters[ch["slug"]] = chapter
                if made:
                    chapter.characters.set(arc.characters.all())
                if ch.get("graph") and not chapter.nodes.exists():
                    self.build_graph(chapter, D.GRAPHS[ch["graph"]], chars, dialogue)

        b = D.BOSS
        boss, made = self.upsert(BossEncounter, {"slug": b["slug"]}, {
            "boss": chars[b["boss"]], "world": worlds[b["world"]],
            "arena": Region.objects.filter(world=worlds[b["world"]], slug=b["arena"]).first(),
            "required_quest": quests[b["quest"]], "title_en": b["title_en"], "title_ar": b["title_ar"],
            "narrative_purpose_en": b["narrative_purpose_en"], "narrative_purpose_ar": b["narrative_purpose_ar"],
            "health_bar_label_en": b["health_bar_label_en"], "health_bar_label_ar": b["health_bar_label_ar"],
            "health_bar_segments": b["segments"], "health_bar_color": b["color"],
            "environmental_changes": b["environmental_changes"],
            "victory_condition_en": b["victory_en"], "victory_condition_ar": b["victory_ar"],
            "defeat_condition_en": b["defeat_en"], "defeat_condition_ar": b["defeat_ar"],
        })
        if made:
            for order, en, ar, threshold, den, dar, line in b["phases"]:
                BossPhase.objects.create(encounter=boss, order=order, name_en=en, name_ar=ar, health_threshold_percent=threshold,
                                         description_en=den, description_ar=dar, dialogue_trigger=dialogue.get(line))
            boss.rewards.set([artifacts["blue-winter-flower"]])

        for c in D.CINEMATICS:
            cin, made = self.upsert(Cinematic, {"slug": c["slug"]}, {
                "title_en": c["title_en"], "title_ar": c["title_ar"], "summary_en": c["summary_en"], "summary_ar": c["summary_ar"],
                "story_chapter": chapters.get(c["chapter"]), "duration_seconds": c["duration"], "unreal_sequence_path": c["unreal"],
            })
            if made:
                cin.characters.set([chars[s] for s in c["characters"]])
                for order, ten, tar, sen, sar, camera, line in c["scenes"]:
                    CinematicScene.objects.create(cinematic=cin, order=order, title_en=ten, title_ar=tar,
                                                  shot_description_en=sen, shot_description_ar=sar, camera_notes=camera,
                                                  dialogue=dialogue.get(line))
        if not boss.intro_cinematic_id:
            boss.intro_cinematic = Cinematic.objects.filter(slug="the-girl-in-the-crystal").first()
            boss.post_battle_cinematic = Cinematic.objects.filter(slug="the-final-garden").first()
            boss.save(update_fields=["intro_cinematic", "post_battle_cinematic", "updated_at"])

        for en, ar, cat in D.GLOSSARY:
            _, made = GlossaryTerm.objects.get_or_create(term_en=en, defaults={"term_ar": ar, "category": cat})
            self.created += int(made)

        for a in D.ANNOUNCEMENTS:
            self.upsert(Announcement, {"slug": a["slug"]}, {
                "category": a["category"], "is_pinned": a["pinned"],
                **{k: a[k] for k in a if k.endswith(("_en", "_ar"))},
            })
        for p in D.PAGES:
            self.upsert(Page, {"slug": p["slug"]}, {"order": p["order"], **{k: p[k] for k in p if k.endswith(("_en", "_ar"))}})

    def build_graph(self, chapter, graph, chars, dialogue):
        nodes = {}
        for order, (key, ntype, start, ending, ten, tar, xen, xar, speaker) in enumerate(graph["nodes"], start=1):
            nodes[key] = StoryNode.objects.create(
                chapter=chapter, key=key, node_type=ntype, is_start=start, ending_type=ending, order=order,
                title_en=ten, title_ar=tar, text_en=xen, text_ar=xar, speaker=chars.get(speaker),
            )
            self.created += 1
        for order, (src, dst, len_, lar, condition, consequences) in enumerate(graph["branches"], start=1):
            StoryBranch.objects.create(from_node=nodes[src], to_node=nodes[dst], label_en=len_, label_ar=lar,
                                       condition=condition, consequences=consequences, order=order)
            self.created += 1
