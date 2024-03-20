from django.urls import path

from . import views

app_name = "post"

urlpatterns = [
    path("", views.upload, name="upload"),
    path(
        "public/<int:post_id>/",
        views.view_post_public,
        name="view_post_public",
    ),
    path("<int:post_id>/", views.view_post_public, name="view_post"),
    path("like/<int:post_id>/", views.like, name="like"),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
]
