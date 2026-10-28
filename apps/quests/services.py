"""Quest state rules (server-side). The game client may report events, but only these functions
decide what a player can start or has completed."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.core.conditions import ConditionContext, evaluate

from .models import PlayerQuestState, Quest, QuestState


def player_context(user, extra=None):
    states = dict(PlayerQuestState.objects.filter(user=user).values_list("quest__slug", "state"))
    ctx = ConditionContext.from_dict(extra or {})
    ctx.quest_states.update(states)
    return ctx


def quest_status_for(user, quest, ctx=None, states=None):
    """Compute the effective state of a quest for a player."""
    states = states if states is not None else dict(
        PlayerQuestState.objects.filter(user=user).values_list("quest_id", "state")
    )
    stored = states.get(quest.pk)
    if stored in {QuestState.ACTIVE, QuestState.COMPLETED, QuestState.FAILED}:
        if stored == QuestState.COMPLETED and quest.is_repeatable:
            return QuestState.AVAILABLE
        return stored
    for dep in quest.dependencies.all():
        if not dep.satisfied_by(states.get(dep.requires_id)):
            return QuestState.LOCKED
    ctx = ctx or player_context(user)
    if not evaluate(quest.start_conditions, ctx):
        return QuestState.LOCKED
    return QuestState.AVAILABLE


def available_quests(user):
    states = dict(PlayerQuestState.objects.filter(user=user).values_list("quest_id", "state"))
    ctx = player_context(user)
    quests = Quest.objects.published().prefetch_related("dependencies")
    return [q for q in quests if quest_status_for(user, q, ctx, states) == QuestState.AVAILABLE]


@transaction.atomic
def start_quest(user, quest):
    if not quest.is_live:
        raise ValidationError("This quest is not published.")
    status = quest_status_for(user, quest)
    if status != QuestState.AVAILABLE:
        raise ValidationError(f"Quest cannot be started (current state: {status}).")
    record, _ = PlayerQuestState.objects.select_for_update().get_or_create(user=user, quest=quest)
    record.state = QuestState.ACTIVE
    record.started_at = timezone.now()
    record.finished_at = None
    record.objective_progress = {}
    record.save()
    return record


@transaction.atomic
def complete_quest(user, quest, ctx_extra=None):
    record = PlayerQuestState.objects.select_for_update().filter(user=user, quest=quest).first()
    if record is None or record.state != QuestState.ACTIVE:
        raise ValidationError("Only an active quest can be completed.")
    required = [o.key for o in quest.objectives.all() if not o.is_optional]
    progress = record.objective_progress or {}
    counts = {o.key: o.required_count for o in quest.objectives.all()}
    unfinished = [key for key in required if int(progress.get(key, 0)) < counts[key]]
    if unfinished:
        raise ValidationError(f"Objectives not finished: {', '.join(unfinished)}.")
    if not evaluate(quest.completion_conditions, player_context(user, ctx_extra)):
        raise ValidationError("Completion conditions are not met.")
    record.state = QuestState.COMPLETED
    record.finished_at = timezone.now()
    record.save()
    return record
