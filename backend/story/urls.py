from django.urls import path
from . import views

app_name = "story"

urlpatterns = [
    path("", views.story, name="upload_story"),
    path("<int:story_id>/", views.get_story, name="get_story"),
    path("delete/<int:story_id>/", views.story, name="delete_story"),
]
