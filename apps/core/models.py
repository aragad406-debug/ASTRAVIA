"""Shared building blocks (abstract models) and cross-cutting records:
site configuration, editable pages, interface text overrides, revisions,
publication records, the audit log, and newsletter subscriptions."""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .text import current_language, normalize_search_text

hex_color = RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Use a six-digit hex colour such as #63E6FF.")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# --------------------------------------------------------------------------- localization
class LocalizedMixin:
    """Models declare `localized_fields = ("name", "summary")` and define `<field>_en` / `<field>_ar`.

    `obj.loc("name")` returns the text in the active language, falling back to English then Arabic.
    """

    localized_fields: tuple = ()

    def loc(self, field, lang=None):
        lang = lang or current_language()
        value = getattr(self, f"{field}_{lang}", "")
        if value:
            return value
        return getattr(self, f"{field}_en", "") or getattr(self, f"{field}_ar", "") or ""

    def loc_pair(self, field):
        return {"en": getattr(self, f"{field}_en", "") or "", "ar": getattr(self, f"{field}_ar", "") or ""}

    def missing_translations(self):
        """Fields authored in one language but empty in the other."""
        missing = []
        for field in self.localized_fields:
            en = (getattr(self, f"{field}_en", "") or "").strip()
            ar = (getattr(self, f"{field}_ar", "") or "").strip()
            if en and not ar:
                missing.append((field, "ar"))
            elif ar and not en:
                missing.append((field, "en"))
        return missing


# --------------------------------------------------------------------------- publication
class ContentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_REVIEW = "in_review", "In review"
    APPROVED = "approved", "Approved"
    SCHEDULED = "scheduled", "Scheduled"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class Visibility(models.TextChoices):
    PUBLIC = "public", "Public"
    TEASER = "teaser", "Public teaser (details obscured)"
    HIDDEN = "hidden", "Hidden"


def published_q(prefix=""):
    now = timezone.now()
    return Q(**{f"{prefix}status": ContentStatus.PUBLISHED}) | Q(
        **{f"{prefix}status": ContentStatus.SCHEDULED, f"{prefix}publish_at__lte": now}
    )


class PublishableQuerySet(models.QuerySet):
    def published(self):
        """Published now, including scheduled items whose time has arrived."""
        return self.filter(published_q())

    def public(self):
        qs = self.published()
        if any(f.name == "visibility" for f in self.model._meta.fields):
            qs = qs.exclude(visibility=Visibility.HIDDEN)
        return qs

    def visible_to(self, user):
        """Public content, plus hidden-but-published content for holders of core.view_hidden_content."""
        if user is not None and user.is_authenticated and user.has_perm("core.view_hidden_content"):
            return self.published()
        return self.public()

    def not_archived(self):
        return self.exclude(status=ContentStatus.ARCHIVED)


class PublishableModel(models.Model):
    status = models.CharField(max_length=12, choices=ContentStatus.choices, default=ContentStatus.DRAFT, db_index=True)
    publish_at = models.DateTimeField(null=True, blank=True, help_text="When status is Scheduled, goes live at this time.")
    published_at = models.DateTimeField(null=True, blank=True, editable=False)
    revision = models.PositiveIntegerField(default=1, editable=False)
    is_seeded = models.BooleanField(default=False, editable=False, help_text="Created by seed_astravia.")

    objects = PublishableQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def is_live(self):
        if self.status == ContentStatus.PUBLISHED:
            return True
        return self.status == ContentStatus.SCHEDULED and self.publish_at is not None and self.publish_at <= timezone.now()


class VisibilityModel(models.Model):
    visibility = models.CharField(max_length=8, choices=Visibility.choices, default=Visibility.PUBLIC, db_index=True)

    class Meta:
        abstract = True


class SearchableModel(models.Model):
    """Keeps a normalized `search_document` so Arabic/English search works on SQLite and PostgreSQL."""

    search_document = models.TextField(blank=True, default="", editable=False)
    search_source_fields: tuple = ()

    class Meta:
        abstract = True

    def build_search_document(self):
        parts = []
        for name in self.search_source_fields:
            for suffix in ("", "_en", "_ar"):
                value = getattr(self, f"{name}{suffix}", None)
                if isinstance(value, str) and value:
                    parts.append(value)
        return normalize_search_text(" ".join(parts))

    def save(self, *args, **kwargs):
        self.search_document = self.build_search_document()
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"search_document"}
        super().save(*args, **kwargs)


# --------------------------------------------------------------------------- site-wide records
class SiteConfiguration(LocalizedMixin, TimeStampedModel):
    """Singleton (pk=1) holding editable homepage copy and site-wide settings."""

    localized_fields = ("hero_title", "hero_intro", "universe_intro", "narrative_intro", "gameplay_intro", "project_status")

    hero_title_en = models.CharField(max_length=200, default="Every world has a memory. Every memory has a price.")
    hero_title_ar = models.CharField(max_length=200, default="لكل عالمٍ ذاكرة... ولكل ذاكرةٍ ثمن.")
    hero_intro_en = models.TextField(blank=True)
    hero_intro_ar = models.TextField(blank=True)
    universe_intro_en = models.TextField(blank=True)
    universe_intro_ar = models.TextField(blank=True)
    narrative_intro_en = models.TextField(blank=True)
    narrative_intro_ar = models.TextField(blank=True)
    gameplay_intro_en = models.TextField(blank=True)
    gameplay_intro_ar = models.TextField(blank=True)
    project_status_en = models.CharField(max_length=200, default="In pre-production: universe, story and content platform.")
    project_status_ar = models.CharField(max_length=200, default="مرحلة ما قبل الإنتاج: الكون والقصة ومنصة المحتوى.")
    trailer_url = models.URLField(blank=True, help_text="Optional https link to an embeddable trailer (opened as a link).")
    trailer_media = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "video"}, help_text="Optional self-hosted trailer video. Never autoplays with sound.",
    )
    ambient_audio = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "audio"}, help_text="Optional ambient loop. Off until the visitor turns it on.",
    )
    contact_email = models.EmailField(blank=True)
    social_links = models.JSONField(default=list, blank=True, help_text='List of {"label": "...", "url": "https://..."}')
    newsletter_enabled = models.BooleanField(default=True)
    copyright_holder = models.CharField(max_length=120, default="ASTRAVIA")

    class Meta:
        verbose_name = "site configuration"
        permissions = [
            ("access_studio", "Can access ASTRAVIA Creator Studio"),
            ("publish_content", "Can publish, unpublish and schedule content"),
            ("review_content", "Can approve content in review"),
            ("view_hidden_content", "Can view hidden worlds, characters and lore"),
            ("manage_team", "Can manage studio members and roles"),
            ("view_audit_log", "Can view the audit log"),
            ("manage_site_settings", "Can edit site configuration"),
        ]
        constraints = [models.CheckConstraint(condition=Q(id=1), name="siteconfiguration_singleton")]

    def __str__(self):
        return "Site configuration"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def clean(self):
        from django.core.exceptions import ValidationError

        if not isinstance(self.social_links, list):
            raise ValidationError({"social_links": "Must be a list."})
        for item in self.social_links:
            if not isinstance(item, dict) or not str(item.get("url", "")).startswith("https://") or not item.get("label"):
                raise ValidationError({"social_links": 'Each link needs a "label" and an https "url".'})


class Page(LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel):
    """Editable standalone pages: privacy policy, terms, cookies, about..."""

    localized_fields = ("title", "body")
    search_source_fields = ("title", "body")

    slug = models.SlugField(max_length=80, unique=True)
    title_en = models.CharField(max_length=160)
    title_ar = models.CharField(max_length=160, blank=True)
    body_en = models.TextField(blank=True)
    body_ar = models.TextField(blank=True)
    show_in_footer = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "slug"]

    def __str__(self):
        return self.title_en

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("core:page", args=[self.slug])


class UIString(TimeStampedModel):
    """Studio-edited override for an interface string defined in apps/core/ui.py."""

    key = models.CharField(max_length=120, unique=True)
    text_en = models.CharField(max_length=500, blank=True)
    text_ar = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["key"]
        verbose_name = "interface text"

    def __str__(self):
        return self.key


class ContentRevision(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    revision_number = models.PositiveIntegerField()
    snapshot = models.JSONField()
    summary = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-revision_number"]
        constraints = [
            models.UniqueConstraint(fields=["content_type", "object_id", "revision_number"], name="unique_revision_number")
        ]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"{self.content_type.model} #{self.object_id} r{self.revision_number}"


class PublicationRecord(models.Model):
    class Action(models.TextChoices):
        SUBMITTED = "submitted", "Submitted for review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Returned to draft"
        PUBLISHED = "published", "Published"
        UNPUBLISHED = "unpublished", "Unpublished"
        SCHEDULED = "scheduled", "Scheduled"
        ARCHIVED = "archived", "Archived"
        RESTORED = "restored", "Revision restored"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    object_repr = models.CharField(max_length=200)
    action = models.CharField(max_length=12, choices=Action.choices)
    from_status = models.CharField(max_length=12, blank=True)
    to_status = models.CharField(max_length=12, blank=True)
    note = models.CharField(max_length=255, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["content_type", "object_id"])]


class AuditEvent(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    actor_label = models.CharField(max_length=254, blank=True, help_text="Kept when the user is later deleted.")
    action = models.CharField(max_length=40, db_index=True)
    target_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    target_id = models.PositiveBigIntegerField(null=True, blank=True)
    target_repr = models.CharField(max_length=200, blank=True)
    summary = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.actor_label} {self.action}"


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    language = models.CharField(max_length=5, default="en")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
