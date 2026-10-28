from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.announcements.models import Announcement
from apps.characters.models import Character
from apps.narrative.models import LoreEntry, StoryArc, StoryChapter

from .models import Page, Visibility, published_q


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["core:home", "worlds:list", "characters:list", "narrative:arcs", "narrative:lore", "announcements:list"]

    def location(self, item):
        return reverse(item)


class _PublicSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    model = None

    def queryset(self):
        # Only fully public content: hidden AND teaser records stay out of the sitemap.
        qs = self.model.objects.published()
        if hasattr(self.model, "visibility"):
            qs = qs.filter(visibility=Visibility.PUBLIC)
        return qs

    def items(self):
        return self.queryset()

    def lastmod(self, obj):
        return obj.updated_at


class WorldSitemap(_PublicSitemap):
    priority = 0.9

    @property
    def model(self):
        from apps.worlds.models import World

        return World


class CharacterSitemap(_PublicSitemap):
    model = Character

    def queryset(self):
        return super().queryset().exclude(category=Character.Category.SECRET)


class ArcSitemap(_PublicSitemap):
    model = StoryArc


class ChapterSitemap(_PublicSitemap):
    model = StoryChapter

    def queryset(self):
        return super().queryset().filter(published_q("arc__"), arc__visibility=Visibility.PUBLIC).select_related("arc")


class LoreSitemap(_PublicSitemap):
    model = LoreEntry


class NewsSitemap(_PublicSitemap):
    model = Announcement


class PageSitemap(_PublicSitemap):
    model = Page
    priority = 0.3


SITEMAPS = {
    "static": StaticSitemap, "worlds": WorldSitemap, "characters": CharacterSitemap, "story": ArcSitemap,
    "chapters": ChapterSitemap, "lore": LoreSitemap, "news": NewsSitemap, "pages": PageSitemap,
}
