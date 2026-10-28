from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.urls import reverse

from apps.core.conditions import condition_validator
from apps.core.models import LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel, VisibilityModel, hex_color


class Character(LocalizedMixin, PublishableModel, VisibilityModel, SearchableModel, TimeStampedModel):
    class Category(models.TextChoices):
        SOVEREIGN = "sovereign", "Sovereign"
        SUPPORTING = "supporting", "Supporting character"
        COMPANION = "companion", "Companion"
        MERCHANT = "merchant", "Merchant"
        GUARDIAN = "guardian", "Guardian"
        BOSS = "boss", "Boss"
        CIVILIAN = "civilian", "Civilian"
        SECRET = "secret", "Secret character"
        GUIDE = "guide", "Celestial guide"
        HISTORICAL = "historical", "Historical figure"

    localized_fields = (
        "name", "title", "teaser", "biography", "appearance", "personality", "motivation", "fears", "secrets",
    )
    search_source_fields = ("name", "title", "teaser", "biography")

    slug = models.SlugField(max_length=80, unique=True)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.SUPPORTING, db_index=True)
    world = models.ForeignKey("worlds.World", null=True, blank=True, on_delete=models.SET_NULL, related_name="characters")
    order = models.PositiveSmallIntegerField(default=0)
    name_en = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120, blank=True)
    title_en = models.CharField(max_length=160, blank=True)
    title_ar = models.CharField(max_length=160, blank=True)
    teaser_en = models.TextField(blank=True, help_text="One or two public lines for cards.")
    teaser_ar = models.TextField(blank=True)
    biography_en = models.TextField(blank=True)
    biography_ar = models.TextField(blank=True)
    appearance_en = models.TextField(blank=True)
    appearance_ar = models.TextField(blank=True)
    personality_en = models.TextField(blank=True)
    personality_ar = models.TextField(blank=True)
    motivation_en = models.TextField(blank=True)
    motivation_ar = models.TextField(blank=True)
    fears_en = models.TextField(blank=True)
    fears_ar = models.TextField(blank=True)
    secrets_en = models.TextField(blank=True, help_text="Studio-only. Never shown on the public site or public API.")
    secrets_ar = models.TextField(blank=True)
    age_years = models.PositiveIntegerField(null=True, blank=True, help_text="Approximate age in years.")
    age_is_unknown = models.BooleanField(default=False)
    transformation_age = models.PositiveIntegerField(null=True, blank=True)
    signature_color = models.CharField(max_length=7, default="#63E6FF", validators=[hex_color])
    portrait = models.ForeignKey(
        "media_library.MediaAsset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        limit_choices_to={"kind": "image"},
    )
    gallery = models.ManyToManyField("media_library.MediaAsset", blank=True, related_name="character_galleries")
    model_3d_reference = models.CharField(max_length=255, blank=True)
    skeletal_mesh_reference = models.CharField(max_length=255, blank=True, help_text="e.g. /Game/Characters/Zerath/SK_Zerath")
    animation_references = models.JSONField(default=list, blank=True, help_text='List of Unreal animation asset paths.')
    unlock_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])

    class Meta:
        ordering = ["order", "name_en"]
        indexes = [models.Index(fields=["status", "visibility", "category"])]

    def __str__(self):
        return self.name_en

    def get_absolute_url(self):
        return reverse("characters:detail", args=[self.slug])

    def clean(self):
        if not isinstance(self.animation_references, list) or not all(isinstance(x, str) for x in self.animation_references):
            raise ValidationError({"animation_references": "Must be a list of text paths."})
        if self.age_is_unknown and self.age_years:
            raise ValidationError({"age_years": "Leave empty when the age is unknown."})

    def relationships(self):
        """Outgoing and incoming relationships as (label, other_character, relationship) tuples."""
        rows = []
        for rel in self.relationships_from.select_related("to_character"):
            rows.append((rel.get_kind_display(), rel.to_character, rel))
        for rel in self.relationships_to.select_related("from_character"):
            rows.append((rel.inverse_label(), rel.from_character, rel))
        return rows


class CharacterRelationship(LocalizedMixin, TimeStampedModel):
    class Kind(models.TextChoices):
        PARENT_OF = "parent_of", "Parent of"
        SIBLING = "sibling", "Sibling of"
        RULER_OF = "ruler_of", "Ruler of"
        ALLY = "ally", "Ally of"
        ENEMY = "enemy", "Enemy of"
        FORMER_ALLY = "former_ally", "Former ally of"
        MENTOR_OF = "mentor_of", "Mentor of"
        GUARDIAN_OF = "guardian_of", "Guardian of"
        MANIPULATES = "manipulates", "Manipulates"
        HISTORICAL = "historical", "Historically connected to"

    INVERSE = {
        "parent_of": "Child of", "ruler_of": "Subject of", "mentor_of": "Student of",
        "guardian_of": "Protected by", "manipulates": "Manipulated by",
    }
    SYMMETRIC = {"sibling", "ally", "enemy", "former_ally", "historical"}

    localized_fields = ("description",)

    from_character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="relationships_from")
    to_character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="relationships_to")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    is_secret = models.BooleanField(default=False, help_text="Secret relationships are not shown publicly.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_character", "to_character", "kind"], name="unique_character_relationship"),
            models.CheckConstraint(condition=~Q(from_character=F("to_character")), name="relationship_not_self"),
        ]

    def __str__(self):
        return f"{self.from_character} — {self.get_kind_display()} — {self.to_character}"

    def inverse_label(self):
        if self.kind in self.SYMMETRIC:
            return self.get_kind_display()
        return self.INVERSE.get(self.kind, self.get_kind_display())

    def clean(self):
        if self.from_character_id and self.from_character_id == self.to_character_id:
            raise ValidationError("A character cannot have a relationship with themselves.")
        if self.kind == self.Kind.PARENT_OF and self.from_character_id and self.to_character_id:
            if CharacterRelationship.objects.filter(
                from_character_id=self.to_character_id, to_character_id=self.from_character_id, kind=self.Kind.PARENT_OF
            ).exclude(pk=self.pk).exists():
                raise ValidationError("Circular parent relationship.")
