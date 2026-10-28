import logging

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST

from apps.announcements.models import Announcement
from apps.characters.models import Character
from apps.dialogues.services import primary_guide
from apps.narrative.models import LoreEntry, StoryArc, StoryChapter
from apps.quests.models import Quest
from apps.worlds.models import World

from .models import NewsletterSubscriber, Page, Visibility, published_q
from .ratelimit import hit
from .text import current_language, normalize_search_text
from .ui import ui
from .visibility import get_for_request

logger = logging.getLogger("astravia")


def home(request):
    worlds = list(
        World.objects.visible_to(request.user).exclude(visibility=Visibility.HIDDEN).select_related("ruler", "hero_image")
    )
    public_worlds = [w for w in worlds if w.visibility == Visibility.PUBLIC]
    teaser_worlds = [w for w in worlds if w.visibility == Visibility.TEASER]
    sovereigns = (
        Character.objects.public().filter(category=Character.Category.SOVEREIGN, visibility=Visibility.PUBLIC)
        .select_related("world", "portrait")
    )
    context = {
        "worlds": public_worlds,
        "teaser_worlds": teaser_worlds,
        "orrery": [
            {"slug": w.slug, "name": w.loc("name"), "color": w.color_primary, "url": w.get_absolute_url()} for w in public_worlds
        ],
        "sovereigns": sovereigns,
        "guide": primary_guide(),
        "heart_lore": LoreEntry.objects.public().filter(slug="heart-of-eternity").first(),
        "main_arc": StoryArc.objects.public().filter(arc_type=StoryArc.ArcType.MAIN).first(),
        "news": Announcement.objects.published()[:3],
        "page_context": "home",
    }
    return render(request, "public/home.html", context)


SEARCH_TYPES = {
    "world": (World, "worlds"),
    "character": (Character, "characters"),
    "chapter": (StoryChapter, "story"),
    "quest": (Quest, "quests"),
    "lore": (LoreEntry, "lore"),
    "news": (Announcement, "news"),
}


def _search(request, query, kind, world_slug):
    terms = [t for t in normalize_search_text(query).split(" ") if len(t) >= 2][:6]
    if not terms:
        return []
    results = []
    for key, (model, _) in SEARCH_TYPES.items():
        if kind and kind != key:
            continue
        qs = model.objects.public() if hasattr(model.objects, "public") else model.objects.published()
        if hasattr(model, "visibility"):
            qs = qs.exclude(visibility=Visibility.TEASER)  # teasers never surface details through search
        if model is StoryChapter:
            qs = qs.filter(published_q("arc__")).exclude(arc__visibility=Visibility.HIDDEN).select_related("arc")
        if model is Character:
            qs = qs.exclude(category=Character.Category.SECRET)
        if world_slug:
            if model is LoreEntry:
                qs = qs.filter(worlds__slug=world_slug)
            elif model is World:
                qs = qs.filter(slug=world_slug)
            elif model is Announcement:
                continue
            else:
                qs = qs.filter(world__slug=world_slug)
        for term in terms:
            qs = qs.filter(search_document__contains=term)
        for obj in qs.distinct()[:30]:
            results.append({"type": key, "obj": obj})
    return results


def search(request):
    query = request.GET.get("q", "").strip()[:120]
    kind = request.GET.get("type", "")
    kind = kind if kind in SEARCH_TYPES else ""
    world_slug = request.GET.get("world", "")
    worlds = World.objects.public().filter(visibility=Visibility.PUBLIC)
    if world_slug and not worlds.filter(slug=world_slug).exists():
        world_slug = ""
    results = _search(request, query, kind, world_slug) if query else []
    page = Paginator(results, 15).get_page(request.GET.get("page"))
    return render(request, "public/search.html", {
        "query": query, "kind": kind, "world_slug": world_slug, "worlds": worlds, "page_obj": page,
        "result_count": len(results), "types": list(SEARCH_TYPES), "page_context": "search",
    })


def page(request, slug):
    obj = get_for_request(request, Page.objects, slug=slug)
    return render(request, "public/page.html", {"page": obj})


@require_POST
def newsletter_subscribe(request):
    next_url = request.POST.get("next") or "/"
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
        next_url = "/"
    email = (request.POST.get("email") or "").strip().lower()[:254]
    if hit(f"newsletter:{request.META.get('REMOTE_ADDR')}", limit=10, window=3600):
        messages.error(request, ui("account.rate_limited"))
        return redirect(next_url)
    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, ui("footer.newsletter.invalid"))
        return redirect(next_url + "#footer")
    NewsletterSubscriber.objects.update_or_create(email=email, defaults={"language": current_language(), "is_active": True})
    # Same message whether or not the address was already subscribed.
    messages.success(request, ui("footer.newsletter.thanks"))
    return redirect(next_url + "#footer")


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "ok"})
    except Exception:
        logger.exception("Health check: database unavailable")
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)


@require_GET
@cache_page(60 * 60)
def robots_txt(request):
    base = settings.SITE_URL or f"{request.scheme}://{request.get_host()}"
    lines = [
        "User-agent: *",
        "Disallow: /creator-studio/",
        "Disallow: /accounts/",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /search/",
        f"Sitemap: {base}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)


def error_500(request):
    return render(request, "errors/500.html", status=500)
