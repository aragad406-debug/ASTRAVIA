from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from apps.core.models import Visibility, published_q
from apps.core.visibility import can_preview, get_for_request
from apps.worlds.models import World

from .models import LoreEntry, StoryArc, StoryChapter


def arc_list(request):
    arcs = StoryArc.objects.visible_to(request.user).select_related("world").prefetch_related("chapters")
    return render(request, "narrative/arc_list.html", {"arcs": arcs, "page_context": "story"})


def _chapters_for(request, arc):
    qs = arc.chapters.all()
    if not (request.GET.get("preview") == "1" and can_preview(request.user, StoryChapter)):
        qs = qs.filter(published_q())
    return qs.order_by("order")


def arc_detail(request, slug):
    arc = get_for_request(request, StoryArc.objects.select_related("world"), slug=slug)
    return render(request, "narrative/arc_detail.html", {"arc": arc, "chapters": _chapters_for(request, arc), "page_context": "story"})


def chapter_detail(request, arc_slug, slug):
    arc = get_for_request(request, StoryArc.objects, slug=arc_slug)
    chapters = _chapters_for(request, arc)
    chapter = chapters.filter(slug=slug).select_related("world").first()
    if chapter is None:
        raise Http404
    request.is_preview = request.is_preview or not chapter.is_live
    return render(request, "narrative/chapter_detail.html", {
        "arc": arc, "chapter": chapter,
        "previous": chapter.previous_chapter(chapters), "next": chapter.next_chapter(chapters),
        "page_context": "story",
    })


def lore_list(request):
    qs = LoreEntry.objects.visible_to(request.user).prefetch_related("worlds")
    world = request.GET.get("world", "")
    entry_type = request.GET.get("type", "")
    if world:
        qs = qs.filter(worlds__slug=world)
    if entry_type in LoreEntry.EntryType.values:
        qs = qs.filter(entry_type=entry_type)
    page = Paginator(qs.distinct(), 18).get_page(request.GET.get("page"))
    present = set(LoreEntry.objects.public().values_list("entry_type", flat=True))
    return render(request, "narrative/lore_list.html", {
        "page_obj": page, "world_filter": world, "type_filter": entry_type,
        "types": [(v, label) for v, label in LoreEntry.EntryType.choices if v in present],
        "worlds": World.objects.public().filter(visibility=Visibility.PUBLIC), "page_context": "lore",
    })


def lore_detail(request, slug):
    entry = get_for_request(request, LoreEntry.objects, slug=slug)
    visible = LoreEntry.objects.visible_to(request.user)
    return render(request, "narrative/lore_detail.html", {
        "entry": entry,
        "teaser": entry.visibility == Visibility.TEASER,
        "related": visible.filter(pk__in=entry.related_entries.values("pk")).exclude(visibility=Visibility.TEASER),
        "worlds": World.objects.visible_to(request.user).filter(pk__in=entry.worlds.values("pk")),
        "page_context": "lore",
    })
