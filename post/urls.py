from django.urls import path

from . import views

app_name = "post"

urlpatterns = [
    path("", views.upload, name="upload"),
    path(
        "anonymous/<int:post_id>/",
        views.view_post_anonymously,
        name="view_post_anonymously",
    ),
    path("<int:post_id>/", views.view_post, name="view_post"),
    path("like/<int:post_id>/", views.like, name="like"),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
]
