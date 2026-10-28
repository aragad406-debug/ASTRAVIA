from django.urls import path

from . import views

app_name = "characters"

urlpatterns = [
    path("", views.character_list, name="list"),
    path("<slug:slug>/", views.character_detail, name="detail"),
]
