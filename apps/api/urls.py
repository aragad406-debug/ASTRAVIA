from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.routers import SimpleRouter
from rest_framework.schemas import get_schema_view

from . import views

app_name = "api"

router = SimpleRouter()
router.register("worlds", views.WorldViewSet, basename="world")
router.register("characters", views.CharacterViewSet, basename="character")
router.register("quests", views.QuestViewSet, basename="quest")
router.register("dialogues", views.DialogueViewSet, basename="dialogue")
router.register("lore", views.LoreViewSet, basename="lore")
router.register("cinematics", views.CinematicViewSet, basename="cinematic")
router.register("encounters", views.EncounterViewSet, basename="encounter")
router.register("story-arcs", views.StoryArcViewSet, basename="storyarc")
router.register("guides", views.GuideViewSet, basename="guide")
router.register("announcements", views.AnnouncementViewSet, basename="announcement")

guide_lines = views.GuideViewSet.as_view({"get": "lines"})

v1 = [
    path("", views.api_root, name="root"),
    path("guides/<slug:slug>/lines/", guide_lines, name="guide-lines"),
    path("localization/", views.localization, name="localization"),
    path("site-config/", views.site_config, name="site-config"),
    path("auth/token/", views.obtain_token, name="token"),
    path("me/", views.me, name="me"),
    path("me/quests/<slug:slug>/", views.player_quest_status, name="me-quest"),
    path("me/quests/<slug:slug>/start/", views.start_player_quest, name="me-quest-start"),
    path(
        "schema/",
        get_schema_view(title="ASTRAVIA Content API", version="1.0.0", renderer_classes=[JSONOpenAPIRenderer],
                        description="Read-only published content for the website and the Unreal Engine 5 client."),
        name="schema",
    ),
    path("", include(router.urls)),
]

urlpatterns = [
    path("v1/", include(v1)),
    path("docs/", TemplateView.as_view(template_name="api/docs.html"), name="docs"),
]
