from django.shortcuts import render

from apps.core.models import Visibility, published_q
from apps.core.visibility import get_for_request, is_teaser
from apps.narrative.models import StoryChapter
from apps.worlds.models import World

from .models import Character

PUBLIC_CATEGORIES = [c for c in Character.Category.values if c != Character.Category.SECRET]


def character_list(request):
    qs = Character.objects.visible_to(request.user).select_related("world", "portrait")
    if not request.user.has_perm("core.view_hidden_content"):
        qs = qs.exclude(category=Character.Category.SECRET, visibility=Visibility.PUBLIC)
    category = request.GET.get("category", "")
    if category in PUBLIC_CATEGORIES:
        qs = qs.filter(category=category)
    world = request.GET.get("world", "")
    if world:
        qs = qs.filter(world__slug=world)
    present = set(Character.objects.public().values_list("category", flat=True))
    categories = [(value, label) for value, label in Character.Category.choices if value in present and value in PUBLIC_CATEGORIES]
    return render(request, "characters/list.html", {
        "characters": qs, "categories": categories, "category": category, "world_filter": world,
        "worlds": World.objects.public().filter(visibility=Visibility.PUBLIC), "page_context": "characters",
    })


def character_detail(request, slug):
    character = get_for_request(request, Character.objects.select_related("world", "portrait"), slug=slug)
    context = {"character": character, "teaser": is_teaser(character), "page_context": "character"}
    if not context["teaser"]:
        visible_ids = set(Character.objects.visible_to(request.user).values_list("pk", flat=True))
        relationships = [
            (label, other, rel) for label, other, rel in character.relationships()
            if not rel.is_secret and other.pk in visible_ids
        ]
        context.update({
            "relationships": relationships,
            "gallery": character.gallery.filter(is_archived=False, kind="image"),
            "chapters": StoryChapter.objects.published().filter(characters=character, arc__visibility=Visibility.PUBLIC)
            .filter(published_q("arc__")).select_related("arc")[:6],
            "world": character.world if character.world and character.world.is_live and character.world.visibility != Visibility.HIDDEN else None,
        })
    return render(request, "characters/detail.html", context)
