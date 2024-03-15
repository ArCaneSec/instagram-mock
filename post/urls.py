from django.urls import path
from . import views

app_name = "post"

urlpatterns = [
    path("", views.upload, name="upload"),
    path("like/<int:post_id>/", views.like, name="like"),
]
