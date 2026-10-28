from django.urls import path

from . import views

app_name = "quests"

urlpatterns = [path("<slug:slug>/", views.quest_detail, name="detail")]
