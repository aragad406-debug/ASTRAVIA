from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.urls import reverse

from apps.core.conditions import condition_validator
from apps.core.models import LocalizedMixin, PublishableModel, SearchableModel, TimeStampedModel, VisibilityModel, hex_color


class QuestState(models.TextChoices):
    LOCKED = "locked", "Locked"
    AVAILABLE = "available", "Available"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class Quest(LocalizedMixin, PublishableModel, VisibilityModel, SearchableModel, TimeStampedModel):
    class QuestType(models.TextChoices):
        MAIN = "main", "Main quest"
        SIDE = "side", "Side quest"
        HIDDEN = "hidden", "Hidden quest"
        CHARACTER = "character", "Character quest"
        EXPLORATION = "exploration", "Exploration quest"
        INVESTIGATION = "investigation", "Investigation quest"
        BOSS = "boss", "Boss quest"
        MEMORY = "memory", "Memory collection quest"
        RESTORATION = "restoration", "World restoration quest"

    localized_fields = ("title", "summary", "description")
    search_source_fields = ("title", "summary", "description")

    slug = models.SlugField(max_length=80, unique=True)
    quest_type = models.CharField(max_length=14, choices=QuestType.choices, default=QuestType.SIDE, db_index=True)
    title_en = models.CharField(max_length=160)
    title_ar = models.CharField(max_length=160, blank=True)
    summary_en = models.TextField(blank=True)
    summary_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    world = models.ForeignKey("worlds.World", null=True, blank=True, on_delete=models.SET_NULL, related_name="quests")
    giver = models.ForeignKey("characters.Character", null=True, blank=True, on_delete=models.SET_NULL, related_name="quests_given")
    characters = models.ManyToManyField("characters.Character", blank=True, related_name="quests")
    order = models.PositiveSmallIntegerField(default=0)
    is_repeatable = models.BooleanField(default=False)
    start_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    completion_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    failure_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    required_items = models.ManyToManyField("narrative.Artifact", blank=True, related_name="required_by_quests")
    cinematics = models.ManyToManyField("narrative.Cinematic", blank=True, related_name="quests")
    unlocks_lore = models.ManyToManyField("narrative.LoreEntry", blank=True, related_name="unlocked_by_quests")

    class Meta:
        ordering = ["world__order", "order", "title_en"]

    def __str__(self):
        return self.title_en

    def get_absolute_url(self):
        return reverse("quests:detail", args=[self.slug])

    def dependency_cycle(self):
        """Return a list of slugs forming a cycle through this quest, or []."""
        graph = {}
        for quest_id, requires_id in QuestDependency.objects.values_list("quest_id", "requires_id"):
            graph.setdefault(quest_id, set()).add(requires_id)
        path, seen = [], set()

        def visit(node):
            if node in path:
                return path[path.index(node):] + [node]
            if node in seen:
                return []
            seen.add(node)
            path.append(node)
            for nxt in graph.get(node, ()):
                found = visit(nxt)
                if found:
                    return found
            path.pop()
            return []

        cycle = visit(self.pk)
        if not cycle:
            return []
        slugs = dict(Quest.objects.filter(pk__in=cycle).values_list("pk", "slug"))
        return [slugs.get(pk, str(pk)) for pk in cycle]


class QuestObjective(LocalizedMixin, TimeStampedModel):
    class ObjectiveType(models.TextChoices):
        REACH = "reach", "Reach a location"
        COLLECT = "collect", "Collect items"
        DEFEAT = "defeat", "Defeat an enemy"
        TALK = "talk", "Talk to a character"
        DISCOVER = "discover", "Discover lore"
        CHOOSE = "choose", "Make a choice"
        CUSTOM = "custom", "Custom (game-defined)"

    localized_fields = ("description",)

    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="objectives")
    key = models.SlugField(max_length=60)
    order = models.PositiveSmallIntegerField(default=0)
    objective_type = models.CharField(max_length=10, choices=ObjectiveType.choices, default=ObjectiveType.CUSTOM)
    description_en = models.CharField(max_length=300)
    description_ar = models.CharField(max_length=300, blank=True)
    target_reference = models.CharField(max_length=160, blank=True, help_text="Slug or game identifier of the target.")
    required_count = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    is_optional = models.BooleanField(default=False)
    completion_condition = models.JSONField(default=dict, blank=True, validators=[condition_validator])

    class Meta:
        ordering = ["quest", "order"]
        constraints = [
            models.UniqueConstraint(fields=["quest", "key"], name="unique_objective_key_per_quest"),
            models.CheckConstraint(condition=Q(required_count__gte=1), name="objective_count_positive"),
        ]

    def __str__(self):
        return f"{self.quest.slug}:{self.key}"


class QuestDependency(TimeStampedModel):
    class Requirement(models.TextChoices):
        COMPLETED = "completed", "Must be completed"
        FAILED = "failed", "Must have failed"
        FINISHED = "finished", "Completed or failed"

    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="dependencies")
    requires = models.ForeignKey(Quest, on_delete=models.PROTECT, related_name="required_by")
    requirement = models.CharField(max_length=10, choices=Requirement.choices, default=Requirement.COMPLETED)

    class Meta:
        verbose_name_plural = "quest dependencies"
        constraints = [
            models.UniqueConstraint(fields=["quest", "requires"], name="unique_quest_dependency"),
            models.CheckConstraint(condition=~Q(quest=F("requires")), name="quest_dependency_not_self"),
        ]

    def __str__(self):
        return f"{self.quest} requires {self.requires}"

    def clean(self):
        if self.quest_id and self.quest_id == self.requires_id:
            raise ValidationError("A quest cannot depend on itself.")
        if self.quest_id and self.requires_id:
            # Would adding quest -> requires create a cycle? i.e. does `requires` already (transitively) need `quest`?
            frontier, seen = [self.requires_id], set()
            while frontier:
                node = frontier.pop()
                if node == self.quest_id:
                    raise ValidationError("This dependency would create a circular quest chain.")
                if node in seen:
                    continue
                seen.add(node)
                frontier.extend(QuestDependency.objects.filter(quest_id=node).exclude(pk=self.pk).values_list("requires_id", flat=True))

    def satisfied_by(self, state):
        if self.requirement == self.Requirement.FINISHED:
            return state in {QuestState.COMPLETED, QuestState.FAILED}
        return state == self.requirement


class QuestReward(LocalizedMixin, TimeStampedModel):
    class RewardType(models.TextChoices):
        ITEM = "item", "Item / artifact"
        LORE = "lore", "Lore discovery"
        TITLE = "title", "Title"
        CURRENCY = "currency", "Currency"
        UNLOCK = "unlock", "Unlock (region, world, ability)"

    localized_fields = ("description",)

    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="rewards")
    reward_type = models.CharField(max_length=10, choices=RewardType.choices)
    artifact = models.ForeignKey("narrative.Artifact", null=True, blank=True, on_delete=models.PROTECT, related_name="+")
    lore = models.ForeignKey("narrative.LoreEntry", null=True, blank=True, on_delete=models.PROTECT, related_name="+")
    amount = models.PositiveIntegerField(default=1)
    description_en = models.CharField(max_length=300, blank=True)
    description_ar = models.CharField(max_length=300, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(reward_type="item") | Q(artifact__isnull=False), name="item_reward_has_artifact"),
            models.CheckConstraint(condition=~Q(reward_type="lore") | Q(lore__isnull=False), name="lore_reward_has_lore"),
        ]

    def __str__(self):
        return f"{self.quest.slug}: {self.get_reward_type_display()}"

    def clean(self):
        if self.reward_type == self.RewardType.ITEM and not self.artifact_id:
            raise ValidationError({"artifact": "Item rewards need an artifact."})
        if self.reward_type == self.RewardType.LORE and not self.lore_id:
            raise ValidationError({"lore": "Lore rewards need a lore entry."})


class PlayerQuestState(TimeStampedModel):
    """Per-player quest state. The server owns this record; game clients never write it directly."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quest_states")
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="player_states")
    state = models.CharField(max_length=10, choices=QuestState.choices, default=QuestState.AVAILABLE)
    objective_progress = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "quest"], name="unique_player_quest_state")]

    def __str__(self):
        return f"{self.user} · {self.quest.slug} · {self.state}"


class BossEncounter(LocalizedMixin, PublishableModel, TimeStampedModel):
    """Structured encounter data for the game client. Combat runs in Unreal Engine, not in Django."""

    localized_fields = ("title", "narrative_purpose", "health_bar_label", "victory_condition", "defeat_condition")

    slug = models.SlugField(max_length=80, unique=True)
    title_en = models.CharField(max_length=160)
    title_ar = models.CharField(max_length=160, blank=True)
    boss = models.ForeignKey("characters.Character", on_delete=models.PROTECT, related_name="boss_encounters")
    world = models.ForeignKey("worlds.World", on_delete=models.PROTECT, related_name="boss_encounters")
    arena = models.ForeignKey("worlds.Region", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    narrative_purpose_en = models.TextField(blank=True)
    narrative_purpose_ar = models.TextField(blank=True)
    intro_cinematic = models.ForeignKey("narrative.Cinematic", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    post_battle_cinematic = models.ForeignKey("narrative.Cinematic", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    required_quest = models.ForeignKey(Quest, null=True, blank=True, on_delete=models.SET_NULL, related_name="boss_encounters")
    required_quest_state = models.CharField(max_length=10, choices=QuestState.choices, default=QuestState.ACTIVE)
    health_bar_label_en = models.CharField(max_length=160, blank=True)
    health_bar_label_ar = models.CharField(max_length=160, blank=True)
    health_bar_segments = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    health_bar_color = models.CharField(max_length=7, default="#8E2439", validators=[hex_color])
    environmental_changes = models.TextField(blank=True)
    victory_condition_en = models.TextField(blank=True)
    victory_condition_ar = models.TextField(blank=True)
    defeat_condition_en = models.TextField(blank=True)
    defeat_condition_ar = models.TextField(blank=True)
    unlock_conditions = models.JSONField(default=dict, blank=True, validators=[condition_validator])
    rewards = models.ManyToManyField("narrative.Artifact", blank=True, related_name="boss_rewards")

    class Meta:
        ordering = ["world__order", "title_en"]

    def __str__(self):
        return self.title_en


class BossPhase(LocalizedMixin, TimeStampedModel):
    localized_fields = ("name", "description")

    encounter = models.ForeignKey(BossEncounter, on_delete=models.CASCADE, related_name="phases")
    order = models.PositiveSmallIntegerField(default=1)
    name_en = models.CharField(max_length=120)
    name_ar = models.CharField(max_length=120, blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    health_threshold_percent = models.PositiveSmallIntegerField(
        default=100, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Phase begins when the boss's health falls to this percentage.",
    )
    dialogue_trigger = models.ForeignKey("dialogues.DialogueEntry", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    environmental_change = models.TextField(blank=True)
    mechanics_notes = models.TextField(blank=True, help_text="Design notes for the Unreal implementation.")

    class Meta:
        ordering = ["encounter", "order"]
        constraints = [
            models.UniqueConstraint(fields=["encounter", "order"], name="unique_phase_order"),
            models.CheckConstraint(condition=Q(health_threshold_percent__lte=100), name="phase_threshold_max_100"),
        ]

    def __str__(self):
        return f"{self.encounter.slug} phase {self.order}"
