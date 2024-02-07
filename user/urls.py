from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("sign-up/", views.sign_up),
    path("login/", views.login, name="login"),
]
