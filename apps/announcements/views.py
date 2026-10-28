from django.core.paginator import Paginator
from django.shortcuts import render

from apps.core.visibility import get_for_request

from .models import Announcement


def announcement_list(request):
    qs = Announcement.objects.published()
    category = request.GET.get("category", "")
    if category in Announcement.Category.values:
        qs = qs.filter(category=category)
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "announcements/list.html", {
        "page_obj": page, "category": category, "categories": Announcement.Category.choices, "page_context": "news",
    })


def announcement_detail(request, slug):
    item = get_for_request(request, Announcement.objects, slug=slug)
    return render(request, "announcements/detail.html", {"item": item, "page_context": "news"})
