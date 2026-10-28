from django.db import models
from django.urls import reverse

from apps.core.models import LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel


class Announcement(LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel):
    class Category(models.TextChoices):
        NEWS = "news", "News"
        DEVLOG = "devlog", "Development update"
        LORE = "lore", "Lore reveal"
        EVENT = "event", "Event"

    localized_fields = ("title", "summary", "body")
    search_source_fields = ("title", "summary", "body")

    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(max_length=8, choices=Category.choices, default=Category.NEWS)
    title_en = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    summary_en = models.TextField(blank=True)
    summary_ar = models.TextField(blank=True)
    body_en = models.TextField(blank=True)
    body_ar = models.TextField(blank=True)
    cover = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "image"},
    )
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-published_at", "-created_at"]

    def __str__(self):
        return self.title_en

    def get_absolute_url(self):
        return reverse("announcements:detail", args=[self.slug])

    @property
    def display_date(self):
        return self.published_at or self.publish_at or self.created_at
