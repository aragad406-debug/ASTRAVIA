from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("p/<slug:slug>/", views.page, name="page"),
    path("newsletter/", views.newsletter_subscribe, name="newsletter"),
]
