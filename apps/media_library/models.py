import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import LocalizedMixin, SearchableModel, TimeStampedModel


def upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    ext = "".join(ch for ch in ext if ch.isalnum())[:5] or "bin"
    return f"astravia/{instance.kind}/{timezone.now():%Y/%m}/{uuid.uuid4().hex}.{ext}"


class MediaAsset(LocalizedMixin, SearchableModel, TimeStampedModel):
    class Kind(models.TextChoices):
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"
        VIDEO = "video", "Video"
        DOCUMENT = "document", "Document (PDF)"
        EXTERNAL = "external", "External reference (3D model, Unreal asset, large file)"

    class Role(models.TextChoices):
        GENERAL = "general", "General"
        PORTRAIT = "portrait", "Character portrait"
        BACKGROUND = "background", "World background"
        GALLERY = "gallery", "Gallery"
        VOICE = "voice", "Voice track"
        MUSIC = "music", "Music"
        TRAILER = "trailer", "Trailer"
        LOGO = "logo", "Logo"
        SOCIAL = "social", "Social sharing image"

    localized_fields = ("alt_text", "description")
    search_source_fields = ("title", "alt_text", "description", "tags")

    title = models.CharField(max_length=160)
    kind = models.CharField(max_length=10, choices=Kind.choices, db_index=True)
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.GENERAL)
    file = models.FileField(upload_to=upload_path, blank=True, max_length=255)
    external_url = models.URLField(blank=True, help_text="For EXTERNAL assets: object-storage URL, Unreal asset path doc, etc.")
    unreal_asset_path = models.CharField(max_length=255, blank=True, help_text="e.g. /Game/Characters/Zerath/SK_Zerath")
    alt_text_en = models.CharField(max_length=300, blank=True)
    alt_text_ar = models.CharField(max_length=300, blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True)
    mime_type = models.CharField(max_length=60, blank=True, editable=False)
    detected_format = models.CharField(max_length=10, blank=True, editable=False)
    size_bytes = models.PositiveBigIntegerField(default=0, editable=False)
    width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    is_generated = models.BooleanField(default=False, help_text="True when produced by an external generator (e.g. TTS).")
    is_archived = models.BooleanField(default=False, db_index=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["kind", "is_archived"])]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(kind="external") | ~models.Q(external_url="") | ~models.Q(unreal_asset_path=""),
                name="external_asset_has_reference",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.get_kind_display()})"

    @property
    def url(self):
        if self.file:
            try:
                return self.file.url
            except ValueError:
                return ""
        return self.external_url

    @property
    def is_missing(self):
        """True when a file-backed asset no longer exists in storage (broken reference)."""
        if self.kind == self.Kind.EXTERNAL:
            return False
        if not self.file:
            return True
        try:
            return not self.file.storage.exists(self.file.name)
        except Exception:  # storage unreachable: report as missing rather than crash the dashboard
            return True
