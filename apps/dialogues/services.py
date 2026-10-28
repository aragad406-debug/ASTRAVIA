"""Rule-based guide dialogue selection. Works with no external services."""
from django.db.models import Q

from apps.core.conditions import ConditionContext, evaluate

from .models import DialogueEntry, GuideAssistant


def primary_guide():
    return (
        GuideAssistant.objects.public().filter(is_primary=True).select_related("character", "character__portrait").first()
    )


def guide_lines(guide, page="any", world_slug=None, ctx: ConditionContext | None = None, limit=6):
    """Published lines for this guide, best match first:
    world-specific lines for the current world, then page-specific lines, then general lines."""
    ctx = ctx or ConditionContext(page=page)
    ctx.page = page
    if world_slug:
        ctx.visited_worlds.add(world_slug)
    qs = (
        DialogueEntry.objects.published()
        .filter(guide=guide)
        .filter(Q(page_context=page) | Q(page_context="any"))
        .select_related("world", "speaker", "voice_en", "voice_ar")
    )
    if world_slug:
        qs = qs.filter(Q(world__isnull=True) | Q(world__slug=world_slug))
    else:
        qs = qs.filter(world__isnull=True)
    lines = [line for line in qs if evaluate(line.conditions, ctx)]

    def score(line):
        return (
            1 if (world_slug and line.world_id) else 0,
            1 if line.page_context == page else 0,
            line.priority,
            1 if line.category == DialogueEntry.Category.GREETING else 0,
        )

    lines.sort(key=score, reverse=True)
    return lines[:limit]
