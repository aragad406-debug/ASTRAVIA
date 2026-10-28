"""Explicit, allow-listed serializers. Studio-only fields (secrets, delivery notes, revision data,
review state) are never listed here, so they can't leak through the public API."""
from rest_framework import serializers

from apps.announcements.models import Announcement
from apps.characters.models import Character
from apps.core.models import SiteConfiguration, Visibility
from apps.dialogues.models import DialogueChoice, DialogueEntry, GuideAssistant
from apps.narrative.models import Cinematic, CinematicScene, LoreEntry, StoryArc, StoryBranch, StoryChapter, StoryNode
from apps.quests.models import BossEncounter, BossPhase, Quest, QuestObjective, QuestReward
from apps.worlds.models import Region, World


class LocalizedField(serializers.Field):
    """Serializes `<base>_en` / `<base>_ar` as {"en": "...", "ar": "..."}."""

    def __init__(self, base=None, **kwargs):
        self.base = base
        kwargs["source"] = "*"
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, obj):
        base = self.base or self.field_name
        return {"en": getattr(obj, f"{base}_en", "") or "", "ar": getattr(obj, f"{base}_ar", "") or ""}


def media_url(asset, request):
    if not asset or getattr(asset, "is_archived", False):
        return None
    url = asset.url
    if url and request is not None and url.startswith("/"):
        return request.build_absolute_uri(url)
    return url or None


def can_see_hidden(context):
    request = context.get("request")
    return bool(request and request.user.is_authenticated and request.user.has_perm("core.view_hidden_content"))


class SlugRef(serializers.Serializer):
    slug = serializers.CharField()


class RegionSerializer(serializers.ModelSerializer):
    name = LocalizedField()
    description = LocalizedField()

    class Meta:
        model = Region
        fields = ["slug", "name", "description", "kind", "order"]


class WorldSerializer(serializers.ModelSerializer):
    name = LocalizedField()
    tagline = LocalizedField()
    short_description = LocalizedField()
    capital = LocalizedField()
    ruler = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    hero_image = serializers.SerializerMethodField()

    class Meta:
        model = World
        fields = ["slug", "order", "visibility", "name", "tagline", "short_description", "capital", "ruler", "theme", "colors", "hero_image"]

    def get_ruler(self, obj):
        r = obj.ruler
        if r and r.is_live and (r.visibility == Visibility.PUBLIC or can_see_hidden(self.context)):
            return r.slug
        return None

    def get_colors(self, obj):
        return {"primary": obj.color_primary, "secondary": obj.color_secondary, "accent": obj.color_accent}

    def get_hero_image(self, obj):
        return media_url(obj.hero_image, self.context.get("request"))

    def to_representation(self, obj):
        if obj.visibility == Visibility.TEASER and not can_see_hidden(self.context):
            return {"slug": obj.slug, "order": obj.order, "visibility": obj.visibility, "theme": obj.theme}
        return super().to_representation(obj)


class WorldDetailSerializer(WorldSerializer):
    description = LocalizedField()
    lore_teaser = LocalizedField()
    environment = LocalizedField()
    regions = serializers.SerializerMethodField()

    class Meta(WorldSerializer.Meta):
        fields = WorldSerializer.Meta.fields + [
            "description", "lore_teaser", "environment", "regions", "unreal_level_path", "model_3d_reference",
        ]

    def get_regions(self, obj):
        qs = obj.regions.all() if can_see_hidden(self.context) else obj.regions.filter(is_secret=False)
        return RegionSerializer(qs, many=True).data


class CharacterSerializer(serializers.ModelSerializer):
    name = LocalizedField()
    title = LocalizedField()
    teaser = LocalizedField()
    world = serializers.SerializerMethodField()
    portrait = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = ["slug", "category", "visibility", "name", "title", "teaser", "world", "signature_color", "portrait"]

    def get_world(self, obj):
        w = obj.world
        if w and w.is_live and (w.visibility != Visibility.HIDDEN or can_see_hidden(self.context)):
            return w.slug
        return None

    def get_portrait(self, obj):
        return media_url(obj.portrait, self.context.get("request"))

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.visibility == Visibility.TEASER and not can_see_hidden(self.context):
            return {k: data[k] for k in ("slug", "category", "visibility", "name", "title", "teaser", "signature_color")}
        return data


class CharacterDetailSerializer(CharacterSerializer):
    biography = LocalizedField()
    appearance = LocalizedField()
    personality = LocalizedField()
    motivation = LocalizedField()
    fears = LocalizedField()
    relationships = serializers.SerializerMethodField()

    class Meta(CharacterSerializer.Meta):
        fields = CharacterSerializer.Meta.fields + [
            "biography", "appearance", "personality", "motivation", "fears", "age_years", "age_is_unknown",
            "transformation_age", "relationships", "model_3d_reference", "skeletal_mesh_reference", "animation_references",
        ]

    def get_relationships(self, obj):
        hidden_ok = can_see_hidden(self.context)
        visible = set(Character.objects.visible_to(self.context["request"].user).values_list("slug", flat=True))
        rows = []
        for label, other, rel in obj.relationships():
            if (rel.is_secret and not hidden_ok) or other.slug not in visible:
                continue
            rows.append({"kind": rel.kind, "label": label, "character": other.slug, "outgoing": rel.from_character_id == obj.pk})
        return rows


class ObjectiveSerializer(serializers.ModelSerializer):
    description = LocalizedField()

    class Meta:
        model = QuestObjective
        fields = ["key", "order", "objective_type", "description", "target_reference", "required_count", "is_optional"]


class RewardSerializer(serializers.ModelSerializer):
    description = LocalizedField()
    artifact = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    lore = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = QuestReward
        fields = ["reward_type", "artifact", "lore", "amount", "description"]


class QuestSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    summary = LocalizedField()
    world = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Quest
        fields = ["slug", "quest_type", "title", "summary", "world", "order", "is_repeatable"]


class QuestDetailSerializer(QuestSerializer):
    description = LocalizedField()
    objectives = ObjectiveSerializer(many=True, read_only=True)
    rewards = RewardSerializer(many=True, read_only=True)
    requires = serializers.SerializerMethodField()
    conditions = serializers.SerializerMethodField()
    required_items = serializers.SlugRelatedField(slug_field="slug", many=True, read_only=True)

    class Meta(QuestSerializer.Meta):
        fields = QuestSerializer.Meta.fields + ["description", "objectives", "rewards", "requires", "required_items", "conditions"]

    def get_requires(self, obj):
        return [{"quest": d.requires.slug, "requirement": d.requirement} for d in obj.dependencies.select_related("requires")]

    def get_conditions(self, obj):
        # Conditions can reference hidden content, so only authorized game services receive them.
        if not can_see_hidden(self.context):
            return None
        return {"start": obj.start_conditions, "completion": obj.completion_conditions, "failure": obj.failure_conditions}


class DialogueChoiceSerializer(serializers.ModelSerializer):
    text = LocalizedField()
    next = serializers.SerializerMethodField()

    class Meta:
        model = DialogueChoice
        fields = ["order", "text", "next", "consequences"]

    def get_next(self, obj):
        nxt = obj.next_entry
        return nxt.key if nxt and nxt.is_live else None


class DialogueSerializer(serializers.ModelSerializer):
    text = LocalizedField()
    speaker = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    world = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    quest = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    choices = DialogueChoiceSerializer(many=True, read_only=True)
    voice = serializers.SerializerMethodField()
    conditions = serializers.SerializerMethodField()

    class Meta:
        model = DialogueEntry
        fields = [
            "key", "speaker", "category", "text", "world", "quest", "trigger_event", "emotion",
            "display_duration_ms", "priority", "subtitles_enabled", "voice", "choices", "conditions",
        ]

    def get_voice(self, obj):
        request = self.context.get("request")
        return {"en": media_url(obj.voice_en, request), "ar": media_url(obj.voice_ar, request)}

    def get_conditions(self, obj):
        return obj.conditions if can_see_hidden(self.context) else None


class LoreSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    summary = LocalizedField()
    timeline_label = LocalizedField()
    worlds = serializers.SerializerMethodField()

    class Meta:
        model = LoreEntry
        fields = ["slug", "entry_type", "visibility", "title", "summary", "timeline_position", "timeline_label", "importance", "worlds"]

    def get_worlds(self, obj):
        hidden_ok = can_see_hidden(self.context)
        return [w.slug for w in obj.worlds.all() if w.is_live and (hidden_ok or w.visibility != Visibility.HIDDEN)]

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.visibility == Visibility.TEASER and not can_see_hidden(self.context):
            data.pop("worlds", None)
        return data


class LoreDetailSerializer(LoreSerializer):
    content = LocalizedField()
    related = serializers.SerializerMethodField()

    class Meta(LoreSerializer.Meta):
        fields = LoreSerializer.Meta.fields + ["content", "related"]

    def get_related(self, obj):
        visible = LoreEntry.objects.visible_to(self.context["request"].user)
        return list(visible.filter(pk__in=obj.related_entries.values("pk")).values_list("slug", flat=True))

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.visibility == Visibility.TEASER and not can_see_hidden(self.context):
            data.pop("content", None)
            data.pop("related", None)
        return data


class SceneSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    shot_description = LocalizedField()
    subtitle = LocalizedField()
    dialogue = serializers.SlugRelatedField(slug_field="key", read_only=True)
    voice_track = serializers.SerializerMethodField()

    class Meta:
        model = CinematicScene
        fields = ["order", "title", "shot_description", "camera_notes", "dialogue", "voice_track", "subtitle",
                  "animation_references", "music_reference", "sound_effects", "duration_seconds"]

    def get_voice_track(self, obj):
        return media_url(obj.voice_track, self.context.get("request"))


class CinematicSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    summary = LocalizedField()
    characters = serializers.SlugRelatedField(slug_field="slug", many=True, read_only=True)
    scenes = SceneSerializer(many=True, read_only=True)
    rendered_video = serializers.SerializerMethodField()

    class Meta:
        model = Cinematic
        fields = ["slug", "title", "summary", "characters", "unreal_sequence_path", "duration_seconds", "render_status",
                  "rendered_video", "scenes"]

    def get_rendered_video(self, obj):
        if obj.render_status != Cinematic.RenderStatus.RENDERED:
            return None
        return media_url(obj.rendered_video, self.context.get("request"))


class PhaseSerializer(serializers.ModelSerializer):
    name = LocalizedField()
    description = LocalizedField()
    dialogue_trigger = serializers.SlugRelatedField(slug_field="key", read_only=True)

    class Meta:
        model = BossPhase
        fields = ["order", "name", "description", "health_threshold_percent", "dialogue_trigger", "environmental_change"]


class EncounterSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    narrative_purpose = LocalizedField()
    health_bar_label = LocalizedField()
    victory_condition = LocalizedField()
    defeat_condition = LocalizedField()
    boss = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    world = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    arena = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    required_quest = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    intro_cinematic = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    post_battle_cinematic = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    rewards = serializers.SlugRelatedField(slug_field="slug", many=True, read_only=True)
    phases = PhaseSerializer(many=True, read_only=True)
    health_bar = serializers.SerializerMethodField()

    class Meta:
        model = BossEncounter
        fields = ["slug", "title", "boss", "world", "arena", "narrative_purpose", "required_quest", "required_quest_state",
                  "intro_cinematic", "post_battle_cinematic", "health_bar_label", "health_bar", "environmental_changes",
                  "victory_condition", "defeat_condition", "rewards", "phases"]

    def get_health_bar(self, obj):
        return {"segments": obj.health_bar_segments, "color": obj.health_bar_color}


class NodeSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    text = LocalizedField()
    speaker = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    dialogue = serializers.SlugRelatedField(slug_field="key", read_only=True)
    cinematic = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = StoryNode
        fields = ["key", "node_type", "is_start", "title", "text", "speaker", "dialogue", "cinematic", "ending_type"]


class BranchSerializer(serializers.ModelSerializer):
    label = LocalizedField()
    source = serializers.CharField(source="from_node.key")
    target = serializers.CharField(source="to_node.key")
    target_chapter = serializers.CharField(source="to_node.chapter.slug")

    class Meta:
        model = StoryBranch
        fields = ["source", "target", "target_chapter", "label", "condition", "consequences", "order"]


class ChapterSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    summary = LocalizedField()

    class Meta:
        model = StoryChapter
        fields = ["slug", "order", "chapter_type", "title", "summary", "ending_type", "is_spoiler"]


class ChapterDetailSerializer(ChapterSerializer):
    body = LocalizedField()
    closing_line = LocalizedField()
    arc = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    graph = serializers.SerializerMethodField()

    class Meta(ChapterSerializer.Meta):
        fields = ChapterSerializer.Meta.fields + ["arc", "body", "closing_line", "graph"]

    def get_graph(self, obj):
        nodes = obj.nodes.select_related("speaker", "dialogue", "cinematic")
        branches = StoryBranch.objects.filter(from_node__chapter=obj).select_related("from_node", "to_node", "to_node__chapter")
        if not can_see_hidden(self.context):
            branch_data = BranchSerializer(branches, many=True).data
            for b in branch_data:
                b["condition"] = None  # conditions may reference hidden content
            return {"nodes": NodeSerializer(nodes, many=True).data, "branches": branch_data}
        return {"nodes": NodeSerializer(nodes, many=True).data, "branches": BranchSerializer(branches, many=True).data}


class ArcSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    summary = LocalizedField()
    world = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = StoryArc
        fields = ["slug", "arc_type", "visibility", "title", "summary", "world", "order"]


class GuideSerializer(serializers.ModelSerializer):
    name = LocalizedField(base="character_name")
    purpose = LocalizedField()
    intro_narration = LocalizedField()
    character = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    related_worlds = serializers.SerializerMethodField()

    class Meta:
        model = GuideAssistant
        fields = ["slug", "character", "name", "purpose", "intro_narration", "supported_languages", "trigger_pages",
                  "display_position", "is_primary", "related_worlds"]

    def get_related_worlds(self, obj):
        return [w.slug for w in obj.related_worlds.all() if w.is_live and w.visibility == Visibility.PUBLIC]

    def to_representation(self, obj):
        obj.character_name_en = obj.character.name_en
        obj.character_name_ar = obj.character.name_ar
        return super().to_representation(obj)


class AnnouncementSerializer(serializers.ModelSerializer):
    title = LocalizedField()
    summary = LocalizedField()
    body = LocalizedField()

    class Meta:
        model = Announcement
        fields = ["slug", "category", "title", "summary", "body", "is_pinned", "published_at"]


class SiteConfigSerializer(serializers.ModelSerializer):
    hero_title = LocalizedField()
    hero_intro = LocalizedField()
    universe_intro = LocalizedField()
    project_status = LocalizedField()

    class Meta:
        model = SiteConfiguration
        fields = ["hero_title", "hero_intro", "universe_intro", "project_status", "contact_email", "social_links"]
