from django.core.cache import cache
from django.test import TestCase
from rest_framework.authtoken.models import Token

from apps.core.models import ContentStatus
from apps.dialogues.models import DialogueEntry
from apps.worlds.models import World

from .helpers import PASSWORD, make_user, seed


class PublicApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed()

    def setUp(self):
        cache.clear()

    def test_root_and_world_list_structure(self):
        self.assertEqual(self.client.get("/api/v1/").status_code, 200)
        data = self.client.get("/api/v1/worlds/").json()
        self.assertEqual(set(data), {"count", "next", "previous", "results"})
        self.assertEqual(data["count"], 5)
        first = data["results"][0]
        self.assertEqual(first["name"], {"en": "Everfrost", "ar": "إيفرفروست"})
        self.assertIn("colors", first)

    def test_world_detail_and_regions(self):
        data = self.client.get("/api/v1/worlds/everfrost/").json()
        self.assertEqual(data["ruler"], "zerath")
        self.assertEqual({r["slug"] for r in data["regions"]}, {"crystalheim", "frozen-gardens", "crystal-throne"})

    def test_pagination(self):
        data = self.client.get("/api/v1/dialogues/?page_size=5").json()
        self.assertEqual(len(data["results"]), 5)
        self.assertIsNotNone(data["next"])
        self.assertEqual(self.client.get("/api/v1/dialogues/?page=999").status_code, 404)

    def test_hidden_content_protected(self):
        self.assertEqual(self.client.get("/api/v1/worlds/umbra/").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/characters/hollow-king/").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/quests/the-gate-that-waits/").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/story-arcs/the-hollow-crown/").status_code, 404)
        body = self.client.get("/api/v1/dialogues/?page_size=100").content.decode()
        self.assertNotIn("hollow-king", body)
        self.assertNotIn("umbra", self.client.get("/api/v1/worlds/").content.decode())

    def test_hidden_content_for_authorized_service_token(self):
        service = make_user("pipeline@example.com", "Narrative Editor")
        token = Token.objects.create(user=service)
        r = self.client.get("/api/v1/worlds/umbra/", HTTP_AUTHORIZATION=f"Token {token.key}")
        self.assertEqual(r.status_code, 200)
        q = self.client.get("/api/v1/quests/shatter-the-crown/", HTTP_AUTHORIZATION=f"Token {token.key}").json()
        self.assertEqual(q["conditions"]["completion"], {"flag": "crown_broken", "equals": True})
        public = self.client.get("/api/v1/quests/shatter-the-crown/").json()
        self.assertIsNone(public["conditions"])

    def test_unpublished_content_protected(self):
        World.objects.filter(slug="solaris").update(status=ContentStatus.DRAFT)
        DialogueEntry.objects.filter(key="kaizen-greeting").update(status=ContentStatus.IN_REVIEW)
        self.assertEqual(self.client.get("/api/v1/worlds/solaris/").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/dialogues/kaizen-greeting/").status_code, 404)

    def test_story_graph_endpoint(self):
        data = self.client.get("/api/v1/story-arcs/the-frozen-promise/chapters/the-crowns-grip/").json()
        keys = {n["key"] for n in data["graph"]["nodes"]}
        self.assertIn("he-remembers", keys)
        self.assertTrue(all(b["condition"] is None for b in data["graph"]["branches"]))

    def test_guide_lines(self):
        data = self.client.get("/api/v1/guides/celestial-guide/lines/?page=world&world=everfrost&lang=ar").json()
        self.assertEqual(data["lines"][0]["key"], "guide-world-everfrost")
        self.assertEqual(data["lines"][0]["lang"], "ar")
        # A hidden world slug is ignored rather than leaking world-specific lines.
        data = self.client.get("/api/v1/guides/celestial-guide/lines/?page=world&world=umbra").json()
        self.assertTrue(all(not l["key"].startswith("guide-world-") for l in data["lines"]))

    def test_invalid_requests(self):
        self.assertEqual(self.client.get("/api/v1/worlds/does-not-exist/").status_code, 404)
        self.assertEqual(self.client.post("/api/v1/worlds/", {"slug": "x"}).status_code, 405)
        self.assertEqual(self.client.get("/api/v1/guides/celestial-guide/lines/?page=" + "x" * 200).status_code, 200)

    def test_localization_and_schema(self):
        data = self.client.get("/api/v1/localization/").json()
        self.assertEqual(data["strings"]["nav.worlds"]["ar"], "العوالم")
        self.assertTrue(any(g["en"] == "Heart of Eternity" for g in data["glossary"]))
        schema = self.client.get("/api/v1/schema/").json()
        self.assertIn("/api/v1/worlds/", schema["paths"])


class PlayerApiTests(TestCase):
    def setUp(self):
        cache.clear()
        seed()
        self.user = make_user("player@example.com")

    def test_me_requires_authentication(self):
        r = self.client.get("/api/v1/me/")
        self.assertIn(r.status_code, (401, 403))

    def test_token_and_server_validated_quest_start(self):
        r = self.client.post("/api/v1/auth/token/", {"email": "player@example.com", "password": PASSWORD}, content_type="application/json")
        token = r.json()["token"]
        auth = {"HTTP_AUTHORIZATION": f"Token {token}"}
        locked = self.client.post("/api/v1/me/quests/letters-to-a-daughter/start/", **auth)
        self.assertEqual(locked.status_code, 400)
        ok = self.client.post("/api/v1/me/quests/the-silent-festival/start/", **auth)
        self.assertEqual(ok.status_code, 201)
        me = self.client.get("/api/v1/me/", **auth).json()
        self.assertEqual(me["quests"][0]["state"], "active")

    def test_token_bad_credentials(self):
        r = self.client.post("/api/v1/auth/token/", {"email": "player@example.com", "password": "nope"}, content_type="application/json")
        self.assertEqual(r.status_code, 400)
