from django.conf import settings
from django.utils.functional import SimpleLazyObject

from .text import current_language, is_rtl


class _LazyOptional:
    """Evaluates on first template use and caches; templates see the object or None-like falsiness."""

    def __init__(self, factory):
        self._factory = factory
        self._loaded = False
        self._value = None

    def _get(self):
        if not self._loaded:
            self._value = self._factory()
            self._loaded = True
        return self._value

    def __bool__(self):
        return self._get() is not None

    def __getattr__(self, name):
        return getattr(self._get(), name)


def _footer_pages():
    from .models import Page

    return list(Page.objects.published().filter(show_in_footer=True).only("slug", "title_en", "title_ar"))


def _site_config():
    from .models import SiteConfiguration

    return SiteConfiguration.load()


def _primary_guide():
    from apps.dialogues.services import primary_guide

    return primary_guide()


def site(request):
    lang = current_language()
    return {
        "LANG": lang,
        "DIR": "rtl" if is_rtl(lang) else "ltr",
        "OTHER_LANG": "en" if lang == "ar" else "ar",
        "SITE_URL": settings.SITE_URL,
        "site_config": SimpleLazyObject(_site_config),
        "footer_pages": SimpleLazyObject(_footer_pages),
        "primary_guide": _LazyOptional(_primary_guide),
        "can_access_studio": request.user.is_authenticated and request.user.has_perm("core.access_studio")
        if hasattr(request, "user") else False,
    }
