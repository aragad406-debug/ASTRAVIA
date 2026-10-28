from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.core.conditions import condition_validator
from apps.core.models import LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel, VisibilityModel
from apps.narrative.models import consequences_validator

PAGE_CONTEXTS = [
    ("any", "Any page"), ("home", "Homepage"), ("worlds", "Worlds index"), ("world", "A world page"),
    ("characters", "Characters index"), ("character", "A character page"), ("story", "Story pages"),
    ("lore", "Lore archive"), ("news", "News"), ("search", "Search"),
]


class VoiceProfile(TimeStampedModel):
    class Provider(models.TextChoices):
        MANUAL = "manual", "Manual upload (no generation)"
        EXTERNAL = "external", "External TTS provider (configured by environment)"

    slug = models.SlugField(max_length=80, unique=True)
    character = models.ForeignKey("characters.Character", on_delete=models.CASCADE, related_name="voice_profiles")
    name = models.CharField(max_length=120)
    provider = models.CharField(max_length=10, choices=Provider.choices, default=Provider.MANUAL)
    provider_voice_id = models.CharField(max_length=120, blank=True, help_text="The provider's voice identifier (not a secret).")
    language = models.CharField(max_length=5, choices=settings.LANGUAGES, default="en")
    description = models.TextField(blank=True)
    pronunciation_notes = models.TextField(blank=True)
    default_emotion = models.CharField(max_length=20, blank=True)
    speaking_rate = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.50")), MaxValueValidator(Decimal("2.00"))],
    )
    pitch_semitones = models.SmallIntegerField(default=0, validators=[MinValueValidator(-12), MaxValueValidator(12)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["character__name_en", "language"]

    def __str__(self):
        return f"{self.name} ({self.language})"


class GuideAssistant(LocalizedMixin, PublishableModel, VisibilityModel, TimeStampedModel):
    """A website/game guide (e.g. the Celestial Guide — مرشدة الكواكب). Dialogue lives in DialogueEntry rows."""

    class Position(models.TextChoices):
        BOTTOM_END = "bottom_end", "Bottom corner (end side)"
        BOTTOM_START = "bottom_start", "Bottom corner (start side)"

    localized_fields = ("purpose", "intro_narration", "voice_description")

    slug = models.SlugField(max_length=80, unique=True)
    character = models.OneToOneField("characters.Character", on_delete=models.PROTECT, related_name="guide_profile")
    purpose_en = models.TextField(blank=True)
    purpose_ar = models.TextField(blank=True)
    intro_narration_en = models.TextField(blank=True)
    intro_narration_ar = models.TextField(blank=True)
    voice_description_en = models.TextField(blank=True)
    voice_description_ar = models.TextField(blank=True)
    voice_profile = models.ForeignKey(VoiceProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    supported_languages = models.JSONField(default=list, blank=True, help_text='e.g. ["en", "ar"]')
    related_worlds = models.ManyToManyField("worlds.World", blank=True, related_name="guides")
    trigger_pages = models.JSONField(default=list, blank=True, help_text='Page contexts where the guide appears, e.g. ["home", "world"]. Empty = all.')
    display_position = models.CharField(max_length=12, choices=Position.choices, default=Position.BOTTOM_END)
    is_primary = models.BooleanField(default=False, help_text="The primary guide appears site-wide.")
    unlock_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    model_3d_reference = models.CharField(max_length=255, blank=True)
    animation_references = models.JSONField(default=list, blank=True)
    ai_enabled = models.BooleanField(
        default=False, help_text="Allow AI-generated replies when GUIDE_AI_PROVIDER is configured. Rule-based lines always work."
    )

    class Meta:
        ordering = ["-is_primary", "slug"]
        constraints = [models.UniqueConstraint(fields=["is_primary"], condition=Q(is_primary=True), name="one_primary_guide")]

    def __str__(self):
        return self.character.name_en if self.character_id else self.slug

    def clean(self):
        valid = {code for code, _ in settings.LANGUAGES}
        if not isinstance(self.supported_languages, list) or not set(self.supported_languages) <= valid:
            raise ValidationError({"supported_languages": f"Use a list containing only {sorted(valid)}."})
        pages = {key for key, _ in PAGE_CONTEXTS}
        if not isinstance(self.trigger_pages, list) or not set(self.trigger_pages) <= pages:
            raise ValidationError({"trigger_pages": f"Use a list of page contexts from {sorted(pages)}."})

    def appears_on(self, page):
        return not self.trigger_pages or "any" in self.trigger_pages or page in self.trigger_pages


class DialogueEntry(LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel):
    class Category(models.TextChoices):
        GREETING = "greeting", "Greeting"
        EXPLORATION = "exploration", "Exploration"
        HINT = "hint", "Hint"
        QUEST_INTRO = "quest_intro", "Quest introduction"
        QUEST_COMPLETE = "quest_complete", "Quest completion"
        WARNING = "warning", "Warning"
        SECRET = "secret", "Secret discovery"
        BOSS_INTRO = "boss_intro", "Boss introduction"
        COMBAT_PHASE = "combat_phase", "Combat phase"
        REVELATION = "revelation", "Emotional revelation"
        MEMORY = "memory", "Memory sequence"
        WORLD_INTRO = "world_intro", "World introduction"
        ENDING = "ending", "Ending"
        HIDDEN_ENDING = "hidden_ending", "Hidden ending"

    class Emotion(models.TextChoices):
        NEUTRAL = "neutral", "Neutral"
        WARM = "warm", "Warm"
        SORROWFUL = "sorrowful", "Sorrowful"
        ANGRY = "angry", "Angry"
        FEARFUL = "fearful", "Fearful"
        HOPEFUL = "hopeful", "Hopeful"
        MYSTERIOUS = "mysterious", "Mysterious"
        COLD = "cold", "Cold"
        DESPERATE = "desperate", "Desperate"

    localized_fields = ("text",)
    search_source_fields = ("text",)

    key = models.SlugField(max_length=100, unique=True, help_text="Stable identifier used by the game client.")
    speaker = models.ForeignKey(
        "characters.Character", null=True, blank=True, on_delete=models.SET_NULL, related_name="dialogue_lines",
        help_text="Empty = narrator.",
    )
    guide = models.ForeignKey(GuideAssistant, null=True, blank=True, on_delete=models.CASCADE, related_name="lines")
    category = models.CharField(max_length=14, choices=Category.choices, default=Category.EXPLORATION, db_index=True)
    text_en = models.TextField(blank=True)
    text_ar = models.TextField(blank=True)
    world = models.ForeignKey("worlds.World", null=True, blank=True, on_delete=models.SET_NULL, related_name="dialogue_lines")
    quest = models.ForeignKey("quests.Quest", null=True, blank=True, on_delete=models.SET_NULL, related_name="dialogue_lines")
    trigger_event = models.CharField(max_length=120, blank=True, help_text="Game event that triggers this line, e.g. enter_region:crystalheim")
    page_context = models.CharField(max_length=12, choices=PAGE_CONTEXTS, default="any", help_text="Website context (guide lines).")
    conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    emotion = models.CharField(max_length=12, choices=Emotion.choices, default=Emotion.NEUTRAL)
    delivery_notes = models.TextField(blank=True)
    display_duration_ms = models.PositiveIntegerField(default=6000, validators=[MinValueValidator(500), MaxValueValidator(60000)])
    priority = models.SmallIntegerField(default=0, help_text="Higher wins when several lines match.")
    voice_en = models.ForeignKey("media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", limit_choices_to={"kind": "audio"})
    voice_ar = models.ForeignKey("media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", limit_choices_to={"kind": "audio"})
    subtitles_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["-priority", "key"]
        verbose_name_plural = "dialogue entries"
        indexes = [models.Index(fields=["guide", "page_context", "status"])]

    def __str__(self):
        speaker = self.speaker.name_en if self.speaker_id else "Narrator"
        return f"{speaker}: {self.key}"

    def clean(self):
        if not (self.text_en or self.text_ar):
            raise ValidationError("Write the line in at least one language.")

    def voice_for(self, lang):
        return self.voice_ar if lang == "ar" else self.voice_en


class DialogueChoice(LocalizedMixin, TimeStampedModel):
    localized_fields = ("text",)

    entry = models.ForeignKey(DialogueEntry, on_delete=models.CASCADE, related_name="choices")
    order = models.PositiveSmallIntegerField(default=0)
    text_en = models.CharField(max_length=300, blank=True)
    text_ar = models.CharField(max_length=300, blank=True)
    next_entry = models.ForeignKey(
        DialogueEntry, null=True, blank=True, on_delete=models.SET_NULL, related_name="incoming_choices",
        help_text="Empty = conversation ends.",
    )
    condition = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    consequences = models.JSONField(default=list, blank=True, validators=[consequences_validator])

    class Meta:
        ordering = ["entry", "order", "id"]

    def __str__(self):
        return f"{self.entry.key} → {self.next_entry.key if self.next_entry_id else 'end'}"

    def clean(self):
        if not (self.text_en or self.text_ar):
            raise ValidationError("Write the choice in at least one language.")
        if self.entry_id and self.next_entry_id and self.entry_id == self.next_entry_id:
            raise ValidationError("A choice cannot lead back to the same line.")


class VoiceGenerationRequest(TimeStampedModel):
    class Status(models.TextChoices):
        NOT_CONFIGURED = "not_configured", "No provider configured"
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    dialogue = models.ForeignKey(DialogueEntry, on_delete=models.CASCADE, related_name="voice_requests")
    voice_profile = models.ForeignKey(VoiceProfile, on_delete=models.CASCADE, related_name="requests")
    language = models.CharField(max_length=5, choices=settings.LANGUAGES)
    text = models.TextField()
    provider = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    error_message = models.CharField(max_length=500, blank=True)
    result_asset = models.ForeignKey("media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.dialogue.key} [{self.language}] {self.status}"
