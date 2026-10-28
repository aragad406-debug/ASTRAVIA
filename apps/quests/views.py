from django.http import Http404
from django.shortcuts import render

from apps.core.visibility import get_for_request

from .models import Quest


def quest_detail(request, slug):
    quest = get_for_request(request, Quest.objects.select_related("world", "giver"), slug=slug)
    if quest.quest_type == Quest.QuestType.HIDDEN and not getattr(request, "is_preview", False) \
            and not request.user.has_perm("core.view_hidden_content"):
        raise Http404
    return render(request, "quests/detail.html", {
        "quest": quest, "objectives": quest.objectives.all(), "page_context": "world",
        "world_slug": quest.world.slug if quest.world else None,
    })
