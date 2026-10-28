from django.db import models
from django.urls import reverse

from apps.core.conditions import condition_validator
from apps.core.models import (
    LocalizedMixin,
    PublishableModel,
    SearchableModel,
    TimeStampedModel,
    VisibilityModel,
    hex_color,
)


class World(LocalizedMixin, PublishableModel, VisibilityModel, SearchableModel, TimeStampedModel):
    class Theme(models.TextChoices):
        FROST = "frost", "Frost (Everfrost)"
        VERDANT = "verdant", "Verdant (living forest)"
        SOLAR = "solar", "Solar (desert)"
        CYBER = "cyber", "Cybernetic (neon city)"
        CELESTIAL = "celestial", "Celestial (observatories)"
        UMBRA = "umbra", "Umbra (memory void)"

    localized_fields = ("name", "tagline", "short_description", "description", "lore_teaser", "environment", "capital")
    search_source_fields = ("name", "tagline", "short_description", "description", "capital")

    slug = models.SlugField(max_length=80, unique=True)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    name_en = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120, blank=True)
    tagline_en = models.CharField(max_length=200, blank=True)
    tagline_ar = models.CharField(max_length=200, blank=True)
    short_description_en = models.TextField(blank=True)
    short_description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    lore_teaser_en = models.TextField(blank=True)
    lore_teaser_ar = models.TextField(blank=True)
    environment_en = models.TextField(blank=True, help_text="Environmental identity: landscapes, architecture, atmosphere.")
    environment_ar = models.TextField(blank=True)
    capital_en = models.CharField(max_length=120, blank=True)
    capital_ar = models.CharField(max_length=120, blank=True)
    ruler = models.ForeignKey(
        "characters.Character", null=True, blank=True, on_delete=models.SET_NULL, related_name="ruled_worlds"
    )
    theme = models.CharField(max_length=10, choices=Theme.choices, default=Theme.CELESTIAL)
    color_primary = models.CharField(max_length=7, default="#63E6FF", validators=[hex_color])
    color_secondary = models.CharField(max_length=7, default="#15234A", validators=[hex_color])
    color_accent = models.CharField(max_length=7, default="#E8C878", validators=[hex_color])
    hero_image = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "image"},
    )
    background_video = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "video"},
    )
    model_3d_reference = models.CharField(max_length=255, blank=True, help_text="External 3D asset reference (not hosted here).")
    unreal_level_path = models.CharField(max_length=255, blank=True, help_text="e.g. /Game/Maps/Everfrost/L_Crystalheim")
    unlock_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])

    class Meta:
        ordering = ["order", "name_en"]
        indexes = [models.Index(fields=["status", "visibility", "order"])]

    def __str__(self):
        return self.name_en

    def get_absolute_url(self):
        return reverse("worlds:detail", args=[self.slug])


class Region(LocalizedMixin, TimeStampedModel):
    class Kind(models.TextChoices):
        CITY = "city", "City"
        WILDERNESS = "wilderness", "Wilderness"
        RUINS = "ruins", "Ruins"
        SANCTUM = "sanctum", "Sanctum / shrine"
        DUNGEON = "dungeon", "Dungeon"
        ARENA = "arena", "Boss arena"
        HIDDEN = "hidden", "Hidden location"

    localized_fields = ("name", "description")

    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name="regions")
    slug = models.SlugField(max_length=80)
    name_en = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120, blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.WILDERNESS)
    order = models.PositiveSmallIntegerField(default=0)
    is_secret = models.BooleanField(default=False, help_text="Secret regions never appear on the public site.")
    unlock_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])

    class Meta:
        ordering = ["world", "order", "name_en"]
        constraints = [models.UniqueConstraint(fields=["world", "slug"], name="unique_region_slug_per_world")]

    def __str__(self):
        return f"{self.name_en} ({self.world.name_en})"
