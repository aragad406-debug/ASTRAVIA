from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views_content as content
from . import views_tools as tools

app_name = "creator_studio"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="creator_studio:dashboard", permanent=False), name="index"),
    path("login/", tools.StudioLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="creator_studio:login"), name="logout"),
    path("dashboard/", tools.dashboard, name="dashboard"),
    path("story/chapters/<int:pk>/flow/", tools.story_flow, name="story_flow"),
    path("dialogue/<int:pk>/preview/", tools.dialogue_preview, name="dialogue_preview"),
    path("dialogue/<int:pk>/voice/", tools.voice_generate, name="voice_generate"),
    path("cinematics/<int:pk>/storyboard/", tools.storyboard, name="storyboard"),
    path("localization/", tools.localization_overview, name="localization"),
    path("localization/missing/", tools.localization_missing, name="localization_missing"),
    path("localization/export/", tools.localization_export, name="localization_export"),
    path("localization/import/", tools.localization_import, name="localization_import"),
    path("localization/interface/", tools.interface_text, name="interface_text"),
    path("localization/<slug:key>/<int:pk>/", tools.localization_compare, name="localization_compare"),
    path("team/", tools.team, name="team"),
    path("team/deletion-requests/", tools.deletion_requests, name="deletion_requests"),
    path("audit/", tools.audit_log, name="audit_log"),
    path("publications/", tools.publication_history, name="publications"),
    path("settings/", tools.site_settings, name="site_settings"),
    # Generic content sections (worlds, characters, quests, dialogue, ...)
    path("content/<slug:key>/", content.content_list, name="content_list"),
    path("content/<slug:key>/new/", content.content_create, name="content_create"),
    path("content/<slug:key>/<int:pk>/", content.content_edit, name="content_edit"),
    path("content/<slug:key>/<int:pk>/delete/", content.content_delete, name="content_delete"),
    path("content/<slug:key>/<int:pk>/revisions/", content.revision_list, name="revision_list"),
    path("content/<slug:key>/<int:pk>/revisions/<int:number>/", content.revision_detail, name="revision_detail"),
    path("content/<slug:key>/<int:pk>/revisions/<int:number>/restore/", content.revision_restore, name="revision_restore"),
    path("content/<slug:key>/<int:pk>/<slug:action>/", content.content_transition, name="content_transition"),
]
