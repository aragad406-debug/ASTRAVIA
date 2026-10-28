from django.urls import path

from . import views

app_name = "narrative"

urlpatterns = [
    path("story/", views.arc_list, name="arcs"),
    path("story/<slug:slug>/", views.arc_detail, name="arc"),
    path("story/<slug:arc_slug>/<slug:slug>/", views.chapter_detail, name="chapter"),
    path("lore/", views.lore_list, name="lore"),
    path("lore/<slug:slug>/", views.lore_detail, name="lore_detail"),
]
