from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("settings/", views.settings, name="settings"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("follow/<int:user_id>/", views.follow, name="follow"),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path(
        "close-friend/<int:user_id>", views.close_friend, name="close_friend"
    ),
    path("settings/", views.settings, name="settings"),
    path("timeline/", views.timeline, name="timeline"),
    path("<str:username>/", views.get_user_data, name="get_user_data"),
]
