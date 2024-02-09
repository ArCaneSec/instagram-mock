from django.urls import path
from . import views

app_name = "post"

urlpatterns = [
    path("", views.upload, name="upload"),
]
