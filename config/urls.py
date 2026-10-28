from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve

from apps.core import views as core_views
from apps.core.sitemaps import SITEMAPS

urlpatterns = [
    path("", include("apps.core.urls")),
    path("worlds/", include("apps.worlds.urls")),
    path("characters/", include("apps.characters.urls")),
    path("", include("apps.narrative.urls")),
    path("quests/", include("apps.quests.urls")),
    path("news/", include("apps.announcements.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("creator-studio/", include("apps.creator_studio.urls")),
    path("api/", include("apps.api.urls")),
    # Django's admin stays available to superusers as a low-level fallback; the Creator Studio is the real tool.
    path("admin/", admin.site.urls),
    path("healthz/", core_views.health, name="health"),
    path("robots.txt", core_views.robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.SERVE_MEDIA and settings.MEDIA_STORAGE == "local":
    # Development, or a Render persistent disk at small scale. Large deployments should use object storage.
    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

handler404 = "apps.core.views.error_404"
handler403 = "apps.core.views.error_403"
handler500 = "apps.core.views.error_500"
