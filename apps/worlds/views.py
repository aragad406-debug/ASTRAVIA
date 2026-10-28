from django.shortcuts import render

from apps.characters.models import Character
from apps.core.models import Visibility
from apps.core.visibility import get_for_request, is_teaser
from apps.narrative.models import LoreEntry, StoryArc
from apps.quests.models import Quest

from .models import World


def world_list(request):
    worlds = World.objects.visible_to(request.user).select_related("ruler", "hero_image")
    return render(request, "worlds/list.html", {"worlds": worlds, "page_context": "worlds"})


def world_detail(request, slug):
    world = get_for_request(request, World.objects.select_related("ruler", "hero_image", "background_video"), slug=slug)
    context = {"world": world, "teaser": is_teaser(world), "page_context": "world", "world_slug": world.slug}
    if not context["teaser"]:
        user = request.user
        context.update({
            "regions": world.regions.filter(is_secret=False),
            "characters": Character.objects.visible_to(user).filter(world=world).exclude(visibility=Visibility.TEASER)
            .exclude(category=Character.Category.SECRET).select_related("portrait"),
            "lore": LoreEntry.objects.visible_to(user).filter(worlds=world).exclude(visibility=Visibility.TEASER)[:6],
            "quests": Quest.objects.visible_to(user).filter(world=world).exclude(quest_type=Quest.QuestType.HIDDEN),
            "arcs": StoryArc.objects.visible_to(user).filter(world=world),
            "ruler": world.ruler if world.ruler and world.ruler.is_live and world.ruler.visibility == Visibility.PUBLIC else None,
            "other_worlds": World.objects.public().filter(visibility=Visibility.PUBLIC).exclude(pk=world.pk),
        })
    return render(request, "worlds/detail.html", context)
