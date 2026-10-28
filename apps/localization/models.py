import hashlib

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TimeStampedModel


class GlossaryTerm(TimeStampedModel):
    """Canonical terminology so proper names are rendered consistently in both languages."""

    class Category(models.TextChoices):
        PERSON = "person", "Character name"
        PLACE = "place", "Place / world"
        TITLE = "title", "Title or rank"
        CONCEPT = "concept", "Concept / artifact"
        INTERFACE = "interface", "Interface term"

    term_en = models.CharField(max_length=120, unique=True)
    term_ar = models.CharField(max_length=120)
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.CONCEPT)
    notes = models.TextField(blank=True, help_text="Usage notes, transliteration decisions, do-not-translate rules.")

    class Meta:
        ordering = ["category", "term_en"]

    def __str__(self):
        return f"{self.term_en} = {self.term_ar}"


def text_fingerprint(*values):
    return hashlib.sha256("\x1f".join(v or "" for v in values).encode("utf-8")).hexdigest()


class TranslationReview(models.Model):
    """Marks one localized field of one record as reviewed. Becomes stale when either language's text changes."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    field = models.CharField(max_length=60)
    fingerprint = models.CharField(max_length=64)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    reviewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["content_type", "object_id", "field"], name="unique_translation_review")
        ]

    def __str__(self):
        return f"{self.content_type.model}#{self.object_id}.{self.field}"
