from django.urls import path

from . import views

app_name = "worlds"

urlpatterns = [
    path("", views.world_list, name="list"),
    path("<slug:slug>/", views.world_detail, name="detail"),
]
