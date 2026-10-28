from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.urls import reverse

from apps.core.conditions import condition_validator
from apps.core.models import LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel, VisibilityModel


class EndingType(models.TextChoices):
    NONE = "", "Not an ending"
    CANONICAL = "canonical", "Canonical ending"
    ALTERNATE = "alternate", "Alternate ending"
    HIDDEN = "hidden", "Hidden ending"
    TRAGIC = "tragic", "Tragic ending"
    FAILURE = "failure", "Failure ending"


class StoryArc(LocalizedMixin, PublishableModel, VisibilityModel, SearchableModel, TimeStampedModel):
    class ArcType(models.TextChoices):
        MAIN = "main", "Main story"
        WORLD = "world", "World story"
        CHARACTER = "character", "Character story"
        SIDE = "side", "Side story"
        SECRET = "secret", "Secret narrative"

    localized_fields = ("title", "summary")
    search_source_fields = ("title", "summary")

    slug = models.SlugField(max_length=80, unique=True)
    arc_type = models.CharField(max_length=10, choices=ArcType.choices, default=ArcType.WORLD)
    title_en = models.CharField(max_length=160)
    title_ar = models.CharField(max_length=160, blank=True)
    summary_en = models.TextField(blank=True)
    summary_ar = models.TextField(blank=True)
    world = models.ForeignKey("worlds.World", null=True, blank=True, on_delete=models.SET_NULL, related_name="story_arcs")
    characters = models.ManyToManyField("characters.Character", blank=True, related_name="story_arcs")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "title_en"]

    def __str__(self):
        return self.title_en

    def get_absolute_url(self):
        return reverse("narrative:arc", args=[self.slug])


class StoryChapter(LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel):
    class ChapterType(models.TextChoices):
        PROLOGUE = "prologue", "Prologue"
        CHAPTER = "chapter", "Chapter"
        EPILOGUE = "epilogue", "Epilogue"
        FLASHBACK = "flashback", "Flashback"
        MEMORY = "memory", "Memory sequence"
        BOSS_INTRO = "boss_intro", "Boss introduction"
        POST_BOSS = "post_boss", "Post-boss scene"
        LORE = "lore", "Optional lore discovery"
        ALTERNATE_ENDING = "alt_ending", "Alternate ending"

    localized_fields = ("title", "summary", "body", "closing_line")
    search_source_fields = ("title", "summary", "body")

    arc = models.ForeignKey(StoryArc, on_delete=models.CASCADE, related_name="chapters")
    slug = models.SlugField(max_length=80)
    order = models.PositiveSmallIntegerField(default=0)
    chapter_type = models.CharField(max_length=12, choices=ChapterType.choices, default=ChapterType.CHAPTER)
    title_en = models.CharField(max_length=160)
    title_ar = models.CharField(max_length=160, blank=True)
    summary_en = models.TextField(blank=True)
    summary_ar = models.TextField(blank=True)
    body_en = models.TextField(blank=True, help_text="Full narrative text. Blank lines separate paragraphs.")
    body_ar = models.TextField(blank=True)
    closing_line_en = models.CharField(max_length=300, blank=True, help_text="Optional final on-screen phrase.")
    closing_line_ar = models.CharField(max_length=300, blank=True)
    world = models.ForeignKey("worlds.World", null=True, blank=True, on_delete=models.SET_NULL, related_name="chapters")
    characters = models.ManyToManyField("characters.Character", blank=True, related_name="chapters")
    prerequisite_quests = models.ManyToManyField("quests.Quest", blank=True, related_name="unlocks_chapters")
    required_discoveries = models.ManyToManyField("narrative.LoreEntry", blank=True, related_name="required_by_chapters")
    unlock_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    ending_type = models.CharField(max_length=10, choices=EndingType.choices, default=EndingType.NONE, blank=True)
    is_spoiler = models.BooleanField(default=False, help_text="Spoiler chapters show only their summary publicly.")

    class Meta:
        ordering = ["arc", "order"]
        constraints = [
            models.UniqueConstraint(fields=["arc", "slug"], name="unique_chapter_slug_per_arc"),
            models.UniqueConstraint(fields=["arc", "order"], name="unique_chapter_order_per_arc"),
        ]

    def __str__(self):
        return f"{self.arc.title_en} — {self.title_en}"

    def get_absolute_url(self):
        return reverse("narrative:chapter", args=[self.arc.slug, self.slug])

    def previous_chapter(self, qs=None):
        qs = qs if qs is not None else self.arc.chapters.all()
        return qs.filter(order__lt=self.order).order_by("-order").first()

    def next_chapter(self, qs=None):
        qs = qs if qs is not None else self.arc.chapters.all()
        return qs.filter(order__gt=self.order).order_by("order").first()


class StoryNode(LocalizedMixin, TimeStampedModel):
    class NodeType(models.TextChoices):
        NARRATION = "narration", "Narration"
        DIALOGUE = "dialogue", "Dialogue"
        CHOICE = "choice", "Player choice"
        CINEMATIC = "cinematic", "Cinematic"
        ENDING = "ending", "Ending"

    localized_fields = ("title", "text")

    chapter = models.ForeignKey(StoryChapter, on_delete=models.CASCADE, related_name="nodes")
    key = models.SlugField(max_length=60, help_text="Stable identifier used by branches and the game client.")
    node_type = models.CharField(max_length=10, choices=NodeType.choices, default=NodeType.NARRATION)
    is_start = models.BooleanField(default=False)
    title_en = models.CharField(max_length=160, blank=True)
    title_ar = models.CharField(max_length=160, blank=True)
    text_en = models.TextField(blank=True)
    text_ar = models.TextField(blank=True)
    speaker = models.ForeignKey("characters.Character", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    dialogue = models.ForeignKey("dialogues.DialogueEntry", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    cinematic = models.ForeignKey("narrative.Cinematic", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    ending_type = models.CharField(max_length=10, choices=EndingType.choices, default=EndingType.NONE, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["chapter", "order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["chapter", "key"], name="unique_node_key_per_chapter"),
            models.UniqueConstraint(fields=["chapter"], condition=Q(is_start=True), name="one_start_node_per_chapter"),
        ]

    def __str__(self):
        return f"{self.chapter.slug}:{self.key}"

    def clean(self):
        if self.node_type == self.NodeType.ENDING and not self.ending_type:
            raise ValidationError({"ending_type": "Ending nodes need an ending type."})
        if self.node_type != self.NodeType.ENDING and self.ending_type:
            raise ValidationError({"ending_type": "Only ending nodes can have an ending type."})


def consequences_validator(value):
    """Consequences are a list of small, declarative state changes applied when a branch is taken."""
    if value in (None, []):
        return
    if not isinstance(value, list) or len(value) > 20:
        raise ValidationError("Consequences must be a list (max 20 entries).")
    allowed = {
        "flag": "set a flag: {\"flag\": \"name\", \"value\": true}",
        "choice": "record a choice: {\"choice\": \"key\", \"value\": \"option\"}",
        "quest": "change quest state: {\"quest\": \"slug\", \"state\": \"active\"}",
        "lore": "discover lore: {\"lore\": \"slug\"}",
        "item": "grant item: {\"item\": \"slug\"}",
    }
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValidationError(f"Consequence {i + 1} must be an object.")
        kinds = set(item) & set(allowed)
        if len(kinds) != 1:
            raise ValidationError(f"Consequence {i + 1}: use exactly one of {sorted(allowed)}.")
        kind = next(iter(kinds))
        if not isinstance(item[kind], str) or not item[kind]:
            raise ValidationError(f"Consequence {i + 1}: '{kind}' must be text.")
        extra = set(item) - {kind, "value", "state"}
        if extra:
            raise ValidationError(f"Consequence {i + 1}: unexpected keys {sorted(extra)}. Expected {allowed[kind]}.")
        if kind == "quest" and item.get("state") not in {"available", "active", "completed", "failed"}:
            raise ValidationError(f"Consequence {i + 1}: quest state must be available, active, completed or failed.")


class StoryBranch(LocalizedMixin, TimeStampedModel):
    localized_fields = ("label",)

    from_node = models.ForeignKey(StoryNode, on_delete=models.CASCADE, related_name="outgoing")
    to_node = models.ForeignKey(StoryNode, on_delete=models.CASCADE, related_name="incoming")
    label_en = models.CharField(max_length=200, blank=True, help_text="Choice text shown to the player (choice nodes).")
    label_ar = models.CharField(max_length=200, blank=True)
    condition = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    consequences = models.JSONField(default=list, blank=True, validators=[consequences_validator])
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["from_node", "order", "id"]
        verbose_name_plural = "story branches"
        constraints = [models.CheckConstraint(condition=~Q(from_node=F("to_node")), name="branch_not_self_loop")]

    def __str__(self):
        return f"{self.from_node} → {self.to_node}"

    def clean(self):
        if self.from_node_id and self.to_node_id:
            if self.from_node_id == self.to_node_id:
                raise ValidationError("A branch cannot point to its own node.")
            if self.from_node.chapter.arc_id != self.to_node.chapter.arc_id:
                raise ValidationError("Branches must stay within one story arc.")


class LoreEntry(LocalizedMixin, PublishableModel, VisibilityModel, SearchableModel, TimeStampedModel):
    class EntryType(models.TextChoices):
        RECORD = "record", "Ancient record"
        MEMORY = "memory", "Memory fragment"
        EVENT = "event", "Historical event"
        FORBIDDEN = "forbidden", "Forbidden knowledge"
        ARTIFACT = "artifact", "Artifact lore"
        PROPHECY = "prophecy", "Prophecy"
        LETTER = "letter", "Letter"
        DIARY = "diary", "Diary"
        MESSAGE = "message", "Archived message"
        DOCUMENT = "document", "Secret document"
        ENVIRONMENT = "environment", "Environmental storytelling"

    class Importance(models.IntegerChoices):
        MINOR = 1, "Minor"
        NOTABLE = 2, "Notable"
        MAJOR = 3, "Major"
        CRITICAL = 4, "Critical to the main mystery"

    localized_fields = ("title", "summary", "content", "timeline_label")
    search_source_fields = ("title", "summary", "content")

    slug = models.SlugField(max_length=80, unique=True)
    entry_type = models.CharField(max_length=12, choices=EntryType.choices, default=EntryType.RECORD)
    title_en = models.CharField(max_length=160)
    title_ar = models.CharField(max_length=160, blank=True)
    summary_en = models.TextField(blank=True)
    summary_ar = models.TextField(blank=True)
    content_en = models.TextField(blank=True)
    content_ar = models.TextField(blank=True)
    worlds = models.ManyToManyField("worlds.World", blank=True, related_name="lore_entries")
    characters = models.ManyToManyField("characters.Character", blank=True, related_name="lore_entries")
    quests = models.ManyToManyField("quests.Quest", blank=True, related_name="lore_entries")
    chapters = models.ManyToManyField(StoryChapter, blank=True, related_name="lore_entries")
    related_entries = models.ManyToManyField("self", blank=True, symmetrical=True)
    discovery_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    timeline_position = models.IntegerField(default=0, help_text="Years relative to the present (negative = past).", db_index=True)
    timeline_label_en = models.CharField(max_length=120, blank=True)
    timeline_label_ar = models.CharField(max_length=120, blank=True)
    importance = models.PositiveSmallIntegerField(choices=Importance.choices, default=Importance.NOTABLE)

    class Meta:
        ordering = ["timeline_position", "title_en"]
        verbose_name_plural = "lore entries"

    def __str__(self):
        return self.title_en

    def get_absolute_url(self):
        return reverse("narrative:lore_detail", args=[self.slug])


class Artifact(LocalizedMixin, TimeStampedModel):
    """Items and artifacts: quest requirements, rewards, collectibles."""

    class Rarity(models.TextChoices):
        COMMON = "common", "Common"
        RARE = "rare", "Rare"
        LEGENDARY = "legendary", "Legendary"
        MYTHIC = "mythic", "Mythic"

    localized_fields = ("name", "description")

    slug = models.SlugField(max_length=80, unique=True)
    name_en = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120, blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    world = models.ForeignKey("worlds.World", null=True, blank=True, on_delete=models.SET_NULL, related_name="artifacts")
    lore_entry = models.ForeignKey(LoreEntry, null=True, blank=True, on_delete=models.SET_NULL, related_name="artifacts")
    rarity = models.CharField(max_length=10, choices=Rarity.choices, default=Rarity.RARE)
    is_key_item = models.BooleanField(default=False)
    icon = models.ForeignKey("media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    unreal_item_id = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["name_en"]

    def __str__(self):
        return self.name_en


class Cinematic(LocalizedMixin, PublishableModel, TimeStampedModel):
    class RenderStatus(models.TextChoices):
        METADATA_ONLY = "metadata", "Metadata only (not produced)"
        IN_PRODUCTION = "production", "In production"
        RENDERED = "rendered", "Rendered video attached"

    localized_fields = ("title", "summary")

    slug = models.SlugField(max_length=80, unique=True)
    title_en = models.CharField(max_length=160)
    title_ar = models.CharField(max_length=160, blank=True)
    summary_en = models.TextField(blank=True)
    summary_ar = models.TextField(blank=True)
    story_chapter = models.ForeignKey(StoryChapter, null=True, blank=True, on_delete=models.SET_NULL, related_name="cinematics")
    characters = models.ManyToManyField("characters.Character", blank=True, related_name="cinematics")
    unreal_sequence_path = models.CharField(max_length=255, blank=True, help_text="e.g. /Game/Cinematics/Everfrost/LS_FinalGarden")
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    trigger_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    render_status = models.CharField(max_length=10, choices=RenderStatus.choices, default=RenderStatus.METADATA_ONLY)
    rendered_video = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "video"},
    )

    class Meta:
        ordering = ["title_en"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(render_status="rendered") | Q(rendered_video__isnull=False),
                name="rendered_cinematic_has_video",
            )
        ]

    def __str__(self):
        return self.title_en

    def clean(self):
        if self.render_status == self.RenderStatus.RENDERED and not self.rendered_video_id:
            raise ValidationError({"rendered_video": "Attach the rendered video before marking the cinematic as rendered."})


class CinematicScene(LocalizedMixin, TimeStampedModel):
    localized_fields = ("title", "shot_description", "subtitle")

    cinematic = models.ForeignKey(Cinematic, on_delete=models.CASCADE, related_name="scenes")
    order = models.PositiveSmallIntegerField(default=0)
    title_en = models.CharField(max_length=160, blank=True)
    title_ar = models.CharField(max_length=160, blank=True)
    shot_description_en = models.TextField(blank=True)
    shot_description_ar = models.TextField(blank=True)
    camera_notes = models.TextField(blank=True)
    dialogue = models.ForeignKey("dialogues.DialogueEntry", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    voice_track = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "audio"},
    )
    subtitle_en = models.TextField(blank=True)
    subtitle_ar = models.TextField(blank=True)
    animation_references = models.CharField(max_length=500, blank=True)
    music_reference = models.CharField(max_length=255, blank=True)
    sound_effects = models.CharField(max_length=500, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["cinematic", "order"]

    def __str__(self):
        return f"{self.cinematic.slug} scene {self.order}"
