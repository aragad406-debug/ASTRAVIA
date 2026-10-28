"""ASTRAVIA public content API, version 1.

Everything here is read-only and returns only published content. Hidden content is returned
only to authenticated principals holding `core.view_hidden_content` (e.g. a server-side build
pipeline using a token) — never via an unguessable URL.
"""
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from apps.announcements.models import Announcement
from apps.characters.models import Character
from apps.core.models import SiteConfiguration, Visibility, published_q
from apps.core.text import current_language
from apps.core.ui import STRINGS, ui
from apps.dialogues.models import DialogueEntry, GuideAssistant
from apps.dialogues.services import guide_lines
from apps.localization.models import GlossaryTerm
from apps.narrative.models import Cinematic, LoreEntry, StoryArc, StoryChapter
from apps.quests.models import BossEncounter, PlayerQuestState, Quest
from apps.quests.services import quest_status_for, start_quest
from apps.worlds.models import World

from . import serializers as s


class ReadOnly(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    list_serializer = None
    detail_serializer = None

    def get_serializer_class(self):
        if self.action == "retrieve" and self.detail_serializer:
            return self.detail_serializer
        return self.list_serializer

    def hidden_ok(self):
        user = self.request.user
        return user.is_authenticated and user.has_perm("core.view_hidden_content")


class WorldViewSet(ReadOnly):
    """Worlds. Teaser worlds return only minimal fields; hidden worlds require authorization."""

    list_serializer = s.WorldSerializer
    detail_serializer = s.WorldDetailSerializer

    def get_queryset(self):
        return World.objects.visible_to(self.request.user).select_related("ruler", "hero_image")


class CharacterViewSet(ReadOnly):
    list_serializer = s.CharacterSerializer
    detail_serializer = s.CharacterDetailSerializer

    def get_queryset(self):
        qs = Character.objects.visible_to(self.request.user).select_related("world", "portrait")
        world = self.request.query_params.get("world")
        category = self.request.query_params.get("category")
        if world:
            qs = qs.filter(world__slug=world)
        if category:
            qs = qs.filter(category=category)
        return qs


class QuestViewSet(ReadOnly):
    list_serializer = s.QuestSerializer
    detail_serializer = s.QuestDetailSerializer

    def get_queryset(self):
        qs = Quest.objects.visible_to(self.request.user).select_related("world").prefetch_related(
            "objectives", "rewards__artifact", "rewards__lore", "required_items"
        )
        if not self.hidden_ok():
            qs = qs.exclude(quest_type=Quest.QuestType.HIDDEN).exclude(world__visibility=Visibility.HIDDEN)
        if self.request.query_params.get("world"):
            qs = qs.filter(world__slug=self.request.query_params["world"])
        return qs


class DialogueViewSet(ReadOnly):
    """Dialogue entries. Filter with ?world=, ?quest=, ?speaker=, ?category=, ?trigger=."""

    lookup_field = "key"
    list_serializer = s.DialogueSerializer

    def get_queryset(self):
        qs = DialogueEntry.objects.published().select_related("speaker", "world", "quest", "voice_en", "voice_ar").prefetch_related(
            "choices__next_entry"
        )
        if not self.hidden_ok():
            qs = qs.exclude(world__visibility=Visibility.HIDDEN).exclude(speaker__visibility=Visibility.HIDDEN).exclude(
                quest__visibility=Visibility.HIDDEN
            )
        p = self.request.query_params
        for param, field in (("world", "world__slug"), ("quest", "quest__slug"), ("speaker", "speaker__slug"),
                             ("category", "category"), ("trigger", "trigger_event")):
            if p.get(param):
                qs = qs.filter(**{field: p[param]})
        return qs


class LoreViewSet(ReadOnly):
    list_serializer = s.LoreSerializer
    detail_serializer = s.LoreDetailSerializer

    def get_queryset(self):
        qs = LoreEntry.objects.visible_to(self.request.user).prefetch_related("worlds")
        if self.request.query_params.get("world"):
            qs = qs.filter(worlds__slug=self.request.query_params["world"])
        return qs.distinct()


class CinematicViewSet(ReadOnly):
    list_serializer = s.CinematicSerializer

    def get_queryset(self):
        qs = Cinematic.objects.published().prefetch_related("characters", "scenes__dialogue", "scenes__voice_track")
        if not self.hidden_ok():
            qs = qs.exclude(characters__visibility=Visibility.HIDDEN)
        return qs.distinct()


class EncounterViewSet(ReadOnly):
    list_serializer = s.EncounterSerializer

    def get_queryset(self):
        qs = BossEncounter.objects.published().select_related(
            "boss", "world", "arena", "required_quest", "intro_cinematic", "post_battle_cinematic"
        ).prefetch_related("phases__dialogue_trigger", "rewards")
        if not self.hidden_ok():
            qs = qs.exclude(boss__visibility=Visibility.HIDDEN).exclude(world__visibility=Visibility.HIDDEN)
        return qs


class StoryArcViewSet(ReadOnly):
    list_serializer = s.ArcSerializer

    def get_queryset(self):
        return StoryArc.objects.visible_to(self.request.user).select_related("world")

    def retrieve(self, request, *args, **kwargs):
        arc = self.get_object()
        data = s.ArcSerializer(arc, context={"request": request}).data
        chapters = arc.chapters.filter(published_q()).order_by("order")
        data["chapters"] = s.ChapterSerializer(chapters, many=True, context={"request": request}).data
        return Response(data)

    @action(detail=True, url_path=r"chapters/(?P<chapter_slug>[-\w]+)")
    def chapter(self, request, slug=None, chapter_slug=None):
        arc = self.get_object()
        chapter = get_object_or_404(StoryChapter.objects.filter(published_q()), arc=arc, slug=chapter_slug)
        return Response(s.ChapterDetailSerializer(chapter, context={"request": request}).data)


class GuideViewSet(ReadOnly):
    list_serializer = s.GuideSerializer

    def get_queryset(self):
        return GuideAssistant.objects.visible_to(self.request.user).select_related("character").prefetch_related("related_worlds")

    @action(detail=True, url_path="lines", url_name="lines")
    def lines(self, request, slug=None):
        """Rule-based guide lines for a page context: ?page=home&world=everfrost&lang=ar"""
        guide = self.get_object()
        page = request.query_params.get("page", "any")[:20]
        world = request.query_params.get("world") or None
        if world and not World.objects.visible_to(request.user).filter(slug=world).exists():
            world = None
        lang = request.query_params.get("lang") or current_language()
        lang = "ar" if lang == "ar" else "en"
        if not guide.appears_on(page):
            return Response({"guide": guide.slug, "lines": []})
        rows = []
        for line in guide_lines(guide, page=page, world_slug=world):
            text = line.text_ar if lang == "ar" else line.text_en
            served = lang if text else ("en" if line.text_en else "ar")
            voice = line.voice_for(served)
            rows.append({
                "key": line.key, "text": text or line.text_en or line.text_ar, "lang": served, "category": line.category,
                "emotion": line.emotion, "duration_ms": line.display_duration_ms,
                "voice_url": s.media_url(voice, request) if voice else None,
            })
        return Response({"guide": guide.slug, "lines": rows})


class AnnouncementViewSet(ReadOnly):
    list_serializer = s.AnnouncementSerializer

    def get_queryset(self):
        return Announcement.objects.published()


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def site_config(request):
    return Response(s.SiteConfigSerializer(SiteConfiguration.load(), context={"request": request}).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def localization(request):
    """Interface strings (with studio overrides applied) and the terminology glossary."""
    strings = {key: {"en": ui(key, lang="en"), "ar": ui(key, lang="ar")} for key in sorted(STRINGS)}
    glossary = [{"en": g.term_en, "ar": g.term_ar, "category": g.category} for g in GlossaryTerm.objects.all()]
    return Response({"languages": ["en", "ar"], "rtl": ["ar"], "strings": strings, "glossary": glossary})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    user = request.user
    states = PlayerQuestState.objects.filter(user=user).select_related("quest")
    return Response({
        "email": user.email,
        "display_name": user.display_name,
        "email_verified": user.email_verified,
        "preferred_language": user.profile.preferred_language,
        "quests": [{"quest": st.quest.slug, "state": st.state, "started_at": st.started_at, "finished_at": st.finished_at} for st in states],
    })


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def start_player_quest(request, slug):
    """Server-validated quest start. The client cannot set quest state directly."""
    quest = get_object_or_404(Quest.objects.visible_to(request.user), slug=slug)
    from django.core.exceptions import ValidationError

    try:
        record = start_quest(request.user, quest)
    except ValidationError as exc:
        raise DRFValidationError({"detail": exc.messages}) from exc
    return Response({"quest": quest.slug, "state": record.state, "started_at": record.started_at}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def player_quest_status(request, slug):
    quest = get_object_or_404(Quest.objects.visible_to(request.user), slug=slug)
    return Response({"quest": quest.slug, "state": quest_status_for(request.user, quest)})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([])
def obtain_token(request):
    """Exchange email + password for an API token (for trusted servers and future player clients)."""
    from django.contrib.auth import authenticate
    from rest_framework.authtoken.models import Token

    from apps.core import ratelimit
    from apps.core.audit import client_ip

    if ratelimit.hit(f"api-token:{client_ip(request)}", limit=10, window=900):
        return Response({"detail": "Too many attempts. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    email = str(request.data.get("email", "")).strip().lower()
    password = str(request.data.get("password", ""))
    user = authenticate(request, username=email, password=password)
    if user is None or not user.is_active:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_root(request):
    from django.urls import reverse

    def url(name):
        return request.build_absolute_uri(reverse(name))

    return Response({
        "version": "v1",
        "worlds": url("api:world-list"), "characters": url("api:character-list"), "quests": url("api:quest-list"),
        "dialogues": url("api:dialogue-list"), "lore": url("api:lore-list"), "cinematics": url("api:cinematic-list"),
        "encounters": url("api:encounter-list"), "story_arcs": url("api:storyarc-list"), "guides": url("api:guide-list"),
        "announcements": url("api:announcement-list"), "localization": url("api:localization"),
        "site_config": url("api:site-config"), "schema": url("api:schema"),
    })
