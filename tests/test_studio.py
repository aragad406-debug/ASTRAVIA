import io
import json

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.core.models import AuditEvent, ContentRevision, ContentStatus, PublicationRecord, UIString
from apps.core.ui import ui
from apps.media_library.models import MediaAsset
from apps.narrative.models import StoryChapter
from apps.worlds.models import World

from .helpers import PASSWORD, make_user, seed

WORLD_FORM = {
    "slug": "glass-sea", "order": 9, "name_en": "The Glass Sea", "name_ar": "البحر الزجاجي", "theme": "frost",
    "visibility": "public", "color_primary": "#63E6FF", "color_secondary": "#15234A", "color_accent": "#E8C878",
    "unlock_conditions": "{}", "region-TOTAL_FORMS": "0", "region-INITIAL_FORMS": "0",
}


class StudioAccessTests(TestCase):
    def setUp(self):
        cache.clear()
        seed()

    def test_unauthenticated_redirects_to_studio_login(self):
        for url in ["/creator-studio/dashboard/", "/creator-studio/content/worlds/", "/creator-studio/team/"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertIn("/creator-studio/login/", r["Location"])

    def test_regular_user_denied(self):
        self.client.force_login(make_user("fan@example.com"))
        self.assertEqual(self.client.get("/creator-studio/dashboard/").status_code, 403)

    def test_studio_login(self):
        make_user("editor@example.com", "World Designer")
        r = self.client.post(reverse("creator_studio:login"), {"username": "editor@example.com", "password": PASSWORD})
        self.assertRedirects(r, reverse("creator_studio:dashboard"))

    def test_role_based_access(self):
        self.client.force_login(make_user("w@example.com", "World Designer"))
        self.assertEqual(self.client.get("/creator-studio/content/worlds/new/").status_code, 200)
        self.assertEqual(self.client.get("/creator-studio/content/quests/new/").status_code, 403)
        self.assertEqual(self.client.get("/creator-studio/team/").status_code, 403)
        self.assertEqual(self.client.get("/creator-studio/audit/").status_code, 403)

    def test_read_only_viewer(self):
        self.client.force_login(make_user("ro@example.com", "Read-Only Viewer"))
        world = World.objects.get(slug="solaris")
        self.assertEqual(self.client.get(f"/creator-studio/content/worlds/{world.pk}/").status_code, 200)
        r = self.client.post(f"/creator-studio/content/worlds/{world.pk}/", {**WORLD_FORM, "slug": "solaris"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.get("/creator-studio/content/worlds/new/").status_code, 403)
        self.assertEqual(self.client.post(f"/creator-studio/content/worlds/{world.pk}/unpublish/").status_code, 403)


class StudioContentTests(TestCase):
    def setUp(self):
        cache.clear()
        seed()

    def test_create_world_records_revision_and_audit(self):
        designer = make_user("w@example.com", "World Designer")
        self.client.force_login(designer)
        r = self.client.post("/creator-studio/content/worlds/new/", WORLD_FORM)
        world = World.objects.get(slug="glass-sea")
        self.assertRedirects(r, f"/creator-studio/content/worlds/{world.pk}/")
        self.assertEqual(world.status, ContentStatus.DRAFT)
        self.assertEqual(ContentRevision.objects.filter(object_id=world.pk, content_type__model="world").count(), 1)
        self.assertTrue(AuditEvent.objects.filter(action="content_created", actor=designer).exists())
        self.assertEqual(self.client.get("/worlds/glass-sea/").status_code, 404)
        self.assertEqual(self.client.get("/worlds/glass-sea/?preview=1").status_code, 200)

    def test_status_cannot_be_set_through_form(self):
        self.client.force_login(make_user("w@example.com", "World Designer"))
        self.client.post("/creator-studio/content/worlds/new/", {**WORLD_FORM, "status": "published"})
        self.assertEqual(World.objects.get(slug="glass-sea").status, ContentStatus.DRAFT)

    def test_publishing_permissions(self):
        designer = make_user("w@example.com", "World Designer")
        reviewer = make_user("r@example.com", "Reviewer")
        world = World.objects.create(slug="draft-w", name_en="Draft W")
        self.client.force_login(designer)
        self.assertEqual(self.client.post(f"/creator-studio/content/worlds/{world.pk}/publish/").status_code, 403)
        world.refresh_from_db()
        self.assertEqual(world.status, ContentStatus.DRAFT)  # refused server-side: no publish permission
        self.client.post(f"/creator-studio/content/worlds/{world.pk}/submit/")
        world.refresh_from_db()
        self.assertEqual(world.status, ContentStatus.IN_REVIEW)
        self.client.force_login(reviewer)
        # Reviewers can approve/publish only content types they can change: they hold no change perms.
        self.assertEqual(self.client.post(f"/creator-studio/content/worlds/{world.pk}/publish/").status_code, 403)
        admin = make_user("a@example.com", "Administrator")
        self.client.force_login(admin)
        self.client.post(f"/creator-studio/content/worlds/{world.pk}/publish/")
        world.refresh_from_db()
        self.assertEqual(world.status, ContentStatus.PUBLISHED)
        self.assertTrue(PublicationRecord.objects.filter(object_id=world.pk, action="published", actor=admin).exists())
        self.assertEqual(self.client.get("/worlds/draft-w/").status_code, 200)

    def test_editing_live_content_requires_publish_permission(self):
        self.client.force_login(make_user("w@example.com", "World Designer"))
        world = World.objects.get(slug="solaris")
        r = self.client.post(f"/creator-studio/content/worlds/{world.pk}/", {**WORLD_FORM, "slug": "solaris"})
        self.assertEqual(r.status_code, 403)

    def test_revision_restore(self):
        admin = make_user("a@example.com", "Administrator")
        self.client.force_login(admin)
        self.client.post("/creator-studio/content/worlds/new/", WORLD_FORM)
        world = World.objects.get(slug="glass-sea")
        self.client.post(f"/creator-studio/content/worlds/{world.pk}/", {**WORLD_FORM, "name_en": "Changed name"})
        world.refresh_from_db()
        self.assertEqual(world.name_en, "Changed name")
        detail = self.client.get(f"/creator-studio/content/worlds/{world.pk}/revisions/1/")
        self.assertContains(detail, "Changed name")
        self.client.post(f"/creator-studio/content/worlds/{world.pk}/revisions/1/restore/")
        world.refresh_from_db()
        self.assertEqual(world.name_en, "The Glass Sea")
        self.assertEqual(world.revision, 3)

    def test_safe_delete(self):
        self.client.force_login(make_user("a@example.com", "Administrator"))
        world = World.objects.get(slug="solaris")
        self.client.post(f"/creator-studio/content/worlds/{world.pk}/delete/")
        self.assertTrue(World.objects.filter(pk=world.pk).exists())  # published
        World.objects.filter(pk=world.pk).update(status=ContentStatus.ARCHIVED)
        self.client.post(f"/creator-studio/content/worlds/{world.pk}/delete/")
        self.assertTrue(World.objects.filter(pk=world.pk).exists())  # linked characters/quests
        empty = World.objects.create(slug="empty", name_en="Empty")
        self.client.post(f"/creator-studio/content/worlds/{empty.pk}/delete/")
        self.assertFalse(World.objects.filter(pk=empty.pk).exists())

    def test_chapter_with_graph_errors_cannot_publish(self):
        self.client.force_login(make_user("a@example.com", "Administrator"))
        chapter = StoryChapter.objects.get(slug="the-crowns-grip")
        chapter.status = ContentStatus.DRAFT
        chapter.save()
        chapter.nodes.filter(key="endless-winter").update(node_type="narration", ending_type="")
        self.client.post(f"/creator-studio/content/chapters/{chapter.pk}/publish/")
        chapter.refresh_from_db()
        self.assertEqual(chapter.status, ContentStatus.DRAFT)

    def test_dashboard_counts_are_real(self):
        self.client.force_login(make_user("a@example.com", "Administrator"))
        r = self.client.get("/creator-studio/dashboard/")
        self.assertEqual(r.context["totals"]["Worlds"], World.objects.count())
        from apps.creator_studio.registry import publishable_models

        before = r.context["status_counts"]["draft"]
        World.objects.create(slug="x1", name_en="X1")
        r = self.client.get("/creator-studio/dashboard/")
        expected = sum(m.objects.filter(status="draft").count() for m in publishable_models())
        self.assertEqual(r.context["status_counts"]["draft"], expected)
        self.assertEqual(r.context["status_counts"]["draft"], before + 1)
        self.assertEqual(r.context["totals"]["Worlds"], World.objects.count())


class StudioMediaTests(TestCase):
    def setUp(self):
        self.client.force_login(make_user("m@example.com", "Media Editor"))

    def _png(self):
        buf = io.BytesIO()
        Image.new("RGB", (8, 6), (10, 20, 30)).save(buf, "PNG")
        return SimpleUploadedFile("portrait.png", buf.getvalue(), content_type="image/png")

    def test_valid_image_upload(self):
        r = self.client.post("/creator-studio/content/media/new/", {
            "title": "Portrait", "kind": "image", "role": "portrait", "file": self._png(), "alt_text_en": "A portrait",
        })
        asset = MediaAsset.objects.get(title="Portrait")
        self.assertEqual(r.status_code, 302)
        self.assertEqual((asset.width, asset.height, asset.detected_format), (8, 6, "png"))

    def test_spoofed_extension_rejected(self):
        fake = SimpleUploadedFile("evil.png", b"<script>alert(1)</script>", content_type="image/png")
        r = self.client.post("/creator-studio/content/media/new/", {"title": "Evil", "kind": "image", "role": "general", "file": fake, "alt_text_en": "x"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(MediaAsset.objects.filter(title="Evil").exists())

    def test_svg_and_missing_alt_rejected(self):
        svg = SimpleUploadedFile("a.svg", b"<svg xmlns='http://www.w3.org/2000/svg'><script/></svg>", content_type="image/svg+xml")
        self.client.post("/creator-studio/content/media/new/", {"title": "SVG", "kind": "image", "role": "general", "file": svg, "alt_text_en": "x"})
        self.client.post("/creator-studio/content/media/new/", {"title": "NoAlt", "kind": "image", "role": "general", "file": self._png()})
        self.assertFalse(MediaAsset.objects.filter(title__in=["SVG", "NoAlt"]).exists())


class StudioToolsTests(TestCase):
    def setUp(self):
        cache.clear()
        seed()
        self.admin = make_user("a@example.com", "Administrator")
        self.client.force_login(self.admin)

    def test_interface_text_override(self):
        self.client.post("/creator-studio/localization/interface/", {"key": "nav.worlds", "text_en": "Realms", "text_ar": ""})
        self.assertTrue(UIString.objects.filter(key="nav.worlds").exists())
        self.assertEqual(ui("nav.worlds", lang="en"), "Realms")
        self.assertEqual(ui("nav.worlds", lang="ar"), "العوالم")

    def test_translation_export_import_roundtrip(self):
        data = json.loads(self.client.get("/creator-studio/localization/export/").content)
        world = World.objects.get(slug="everfrost")
        record = next(r for r in data["records"] if r["model"] == "worlds.world" and r["pk"] == world.pk)
        record["fields"]["tagline"]["ar"] = "سطرٌ جديد"
        payload = json.dumps({"records": [record, {"model": "accounts.user", "pk": 1, "fields": {"email": {"en": "x"}}}]}).encode()
        r = self.client.post("/creator-studio/localization/import/", {"file": SimpleUploadedFile("t.json", payload)})
        self.assertEqual(r.context["report"]["updated"], 1)
        self.assertEqual(r.context["report"]["skipped"], 1)
        world.refresh_from_db()
        self.assertEqual(world.tagline_ar, "سطرٌ جديد")

    def test_team_cannot_grant_owner(self):
        r = self.client.post("/creator-studio/team/", {"email": "new@example.com", "roles": []})
        self.assertEqual(r.status_code, 302)
        from django.contrib.auth.models import Group

        owner = Group.objects.get(name="Owner")
        r = self.client.post("/creator-studio/team/", {"email": "new@example.com", "roles": [owner.pk]})
        self.assertEqual(r.status_code, 200)  # invalid choice for non-superusers
        self.assertTrue(AuditEvent.objects.filter(action="roles_changed").exists())

    def test_dialogue_preview_evaluates_conditions(self):
        from apps.dialogues.models import DialogueEntry

        entry = DialogueEntry.objects.get(key="zerath-boss-intro")
        r = self.client.get(f"/creator-studio/dialogue/{entry.pk}/preview/", {"language": "ar", "flags": "{}"})
        self.assertTrue(r.context["result"]["entry_passes"])
        self.assertEqual(r.context["result"]["text"], entry.text_ar)

    def test_voice_generation_without_provider_is_not_reported_as_success(self):
        from apps.dialogues.models import DialogueEntry, VoiceGenerationRequest, VoiceProfile

        entry = DialogueEntry.objects.get(key="guide-home-greeting")
        vp = VoiceProfile.objects.get(slug="celestial-guide-en")
        self.client.post(f"/creator-studio/dialogue/{entry.pk}/voice/", {"voice_profile": vp.pk, "language": "en"})
        req = VoiceGenerationRequest.objects.get(dialogue=entry)
        self.assertEqual(req.status, VoiceGenerationRequest.Status.NOT_CONFIGURED)
        self.assertIsNone(req.result_asset)
