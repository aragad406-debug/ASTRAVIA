"""Creator Studio section registry.

Each Section describes one content type: which fields editors see, how lists are searched and
filtered, which child records are edited inline, and where its public preview lives. Generic
views (views_content.py) turn these descriptions into permission-checked CRUD screens with
revisions, publication workflow and audit logging.
"""
from dataclasses import dataclass, field
from typing import Callable

from apps.announcements.models import Announcement
from apps.characters.models import Character, CharacterRelationship
from apps.core.models import Page, PublishableModel
from apps.dialogues.models import DialogueChoice, DialogueEntry, GuideAssistant, VoiceProfile
from apps.localization.models import GlossaryTerm
from apps.media_library.models import MediaAsset
from apps.narrative.models import Artifact, Cinematic, CinematicScene, LoreEntry, StoryArc, StoryChapter, StoryNode
from apps.quests.models import BossEncounter, BossPhase, Quest, QuestDependency, QuestObjective, QuestReward
from apps.worlds.models import Region, World

STUDIO_EXCLUDE = {"status", "publish_at", "published_at", "revision", "is_seeded", "search_document", "created_at", "updated_at"}


@dataclass
class Inline:
    model: type
    fields: list
    label: str
    fk_name: str | None = None
    extra: int = 1


@dataclass
class Section:
    key: str
    model: type
    label: str
    label_ar: str
    group: str
    list_display: list
    search_fields: list
    fields: list | None = None  # None = every editable field except STUDIO_EXCLUDE
    filters: list = field(default_factory=list)
    inlines: list = field(default_factory=list)
    preview: Callable | None = None
    ordering: list | None = None
    form_class: type | None = None

    @property
    def publishable(self):
        return issubclass(self.model, PublishableModel)

    @property
    def perm_prefix(self):
        return f"{self.model._meta.app_label}.%s_{self.model._meta.model_name}"

    def perm(self, action):
        return self.perm_prefix % action

    def preview_url(self, obj):
        if self.preview is None:
            return None
        try:
            url = self.preview(obj)
        except Exception:
            return None
        return f"{url}?preview=1" if url else None


GROUPS = [
    ("universe", "Universe", "الكون"),
    ("story", "Story", "القصة"),
    ("gameplay", "Gameplay", "اللعب"),
    ("voice", "Dialogue & voice", "الحوار والصوت"),
    ("site", "Website", "الموقع"),
    ("localization", "Localization", "الترجمة"),
]

SECTIONS = [
    Section(
        "worlds", World, "Worlds", "العوالم", "universe",
        list_display=["name_en", "name_ar", "order", "visibility", "ruler"], search_fields=["name_en", "name_ar", "slug"],
        filters=["visibility", "theme"], preview=lambda o: o.get_absolute_url(),
        inlines=[Inline(Region, ["slug", "name_en", "name_ar", "kind", "order", "description_en", "description_ar", "is_secret", "unlock_conditions"], "Exploration regions")],
    ),
    Section(
        "characters", Character, "Characters", "الشخصيات", "universe",
        list_display=["name_en", "name_ar", "category", "world", "visibility"], search_fields=["name_en", "name_ar", "slug", "title_en"],
        filters=["category", "visibility", "world"], preview=lambda o: o.get_absolute_url(),
        inlines=[Inline(CharacterRelationship, ["to_character", "kind", "description_en", "description_ar", "is_secret"], "Relationships (from this character)", fk_name="from_character")],
    ),
    Section(
        "lore", LoreEntry, "Lore & memory archive", "أرشيف الذاكرة", "universe",
        list_display=["title_en", "entry_type", "importance", "timeline_position", "visibility"], search_fields=["title_en", "title_ar", "slug"],
        filters=["entry_type", "visibility", "importance"], preview=lambda o: o.get_absolute_url(),
    ),
    Section(
        "artifacts", Artifact, "Artifacts & items", "القطع الأثرية", "universe",
        list_display=["name_en", "name_ar", "rarity", "world", "is_key_item"], search_fields=["name_en", "name_ar", "slug"], filters=["rarity", "world"],
    ),
    Section(
        "arcs", StoryArc, "Story arcs", "الأقواس القصصية", "story",
        list_display=["title_en", "arc_type", "world", "order", "visibility"], search_fields=["title_en", "title_ar", "slug"],
        filters=["arc_type", "visibility", "world"], preview=lambda o: o.get_absolute_url(),
    ),
    Section(
        "chapters", StoryChapter, "Story chapters", "الفصول", "story",
        list_display=["title_en", "arc", "order", "chapter_type", "ending_type"], search_fields=["title_en", "title_ar", "slug"],
        filters=["arc", "chapter_type"], preview=lambda o: o.get_absolute_url(), ordering=["arc__order", "order"],
        inlines=[Inline(StoryNode, ["key", "node_type", "is_start", "order", "title_en", "title_ar", "text_en", "text_ar", "speaker", "dialogue", "cinematic", "ending_type"], "Story nodes (branches are edited in the flow editor)")],
    ),
    Section(
        "cinematics", Cinematic, "Cinematics", "المشاهد السينمائية", "story",
        list_display=["title_en", "story_chapter", "render_status", "duration_seconds"], search_fields=["title_en", "title_ar", "slug"],
        filters=["render_status"],
        inlines=[Inline(CinematicScene, ["order", "title_en", "title_ar", "shot_description_en", "shot_description_ar", "camera_notes", "dialogue", "voice_track", "subtitle_en", "subtitle_ar", "animation_references", "music_reference", "sound_effects", "duration_seconds"], "Storyboard scenes")],
    ),
    Section(
        "quests", Quest, "Quests", "المهام", "gameplay",
        list_display=["title_en", "quest_type", "world", "order", "visibility"], search_fields=["title_en", "title_ar", "slug"],
        filters=["quest_type", "world", "visibility"], preview=lambda o: o.get_absolute_url(),
        inlines=[
            Inline(QuestObjective, ["key", "order", "objective_type", "description_en", "description_ar", "target_reference", "required_count", "is_optional", "completion_condition"], "Objectives"),
            Inline(QuestDependency, ["requires", "requirement"], "Prerequisite quests", fk_name="quest"),
            Inline(QuestReward, ["reward_type", "artifact", "lore", "amount", "description_en", "description_ar"], "Rewards"),
        ],
    ),
    Section(
        "encounters", BossEncounter, "Boss encounters", "مواجهات الزعماء", "gameplay",
        list_display=["title_en", "boss", "world", "required_quest"], search_fields=["title_en", "title_ar", "slug"], filters=["world"],
        inlines=[Inline(BossPhase, ["order", "name_en", "name_ar", "health_threshold_percent", "description_en", "description_ar", "dialogue_trigger", "environmental_change", "mechanics_notes"], "Phases")],
    ),
    Section(
        "dialogue", DialogueEntry, "Dialogue", "الحوار", "voice",
        list_display=["key", "speaker", "category", "world", "page_context"], search_fields=["key", "text_en", "text_ar", "trigger_event"],
        filters=["category", "speaker", "world", "guide"],
        inlines=[Inline(DialogueChoice, ["order", "text_en", "text_ar", "next_entry", "condition", "consequences"], "Response choices", fk_name="entry")],
    ),
    Section(
        "guides", GuideAssistant, "Guide assistants", "المرشدون", "voice",
        list_display=["character", "is_primary", "display_position", "visibility"], search_fields=["slug", "character__name_en"],
    ),
    Section(
        "voices", VoiceProfile, "Voice profiles", "الأصوات", "voice",
        list_display=["name", "character", "language", "provider", "is_active"], search_fields=["name", "slug", "character__name_en"],
        filters=["language", "provider"],
    ),
    Section(
        "announcements", Announcement, "Announcements", "الإعلانات", "site",
        list_display=["title_en", "category", "is_pinned", "publish_at"], search_fields=["title_en", "title_ar", "slug"],
        filters=["category"], preview=lambda o: o.get_absolute_url(),
    ),
    Section(
        "pages", Page, "Pages", "الصفحات", "site",
        list_display=["title_en", "slug", "show_in_footer", "order"], search_fields=["title_en", "title_ar", "slug"],
        preview=lambda o: o.get_absolute_url(),
    ),
    Section(
        "media", MediaAsset, "Media library", "مكتبة الوسائط", "site",
        list_display=["title", "kind", "role", "size_bytes", "is_archived"], search_fields=["title", "tags", "alt_text_en"],
        filters=["kind", "role", "is_archived"],
        fields=["title", "kind", "role", "file", "external_url", "unreal_asset_path", "alt_text_en", "alt_text_ar",
                "description_en", "description_ar", "tags", "is_archived"],
    ),
    Section(
        "glossary", GlossaryTerm, "Terminology glossary", "مسرد المصطلحات", "localization",
        list_display=["term_en", "term_ar", "category"], search_fields=["term_en", "term_ar"], filters=["category"],
    ),
]

BY_KEY = {s.key: s for s in SECTIONS}
BY_MODEL = {s.model: s for s in SECTIONS}


def get_section(key):
    return BY_KEY.get(key)


def section_for(obj_or_model):
    model = obj_or_model if isinstance(obj_or_model, type) else type(obj_or_model)
    return BY_MODEL.get(model)


def publishable_models():
    return [s.model for s in SECTIONS if s.publishable]


def localized_models():
    """Models whose localized fields the Localization Studio tracks."""
    seen, out = set(), []
    for s in SECTIONS:
        if getattr(s.model, "localized_fields", ()) and s.model not in seen:
            seen.add(s.model)
            out.append(s)
    return out
