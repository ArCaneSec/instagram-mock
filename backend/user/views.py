import datetime

import redis
from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from post import models as pm
from post.serializers import PostSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils import auth_utils as au

from . import authenticate as auth
from . import core
from . import models as m
from . import serializers as s
from .authenticate import authenticate
from .models import User
from .tasks import send_forget_password_email

# Create your views here.

r = redis.Redis(settings.REDIS_BACKEND_HOST, settings.REDIS_BACKEND_PORT)


@api_view(["POST"])
def sign_up(request):
    """
    User's will create new account from this endpoint.

    Request's body schema:
        'username' (str)
        'firstName' (str)
        'lastName' (str)
        'nickName' (Optional[str])
        'profile' (Optional[str])
        'phoneNumber' (Optional[str])
        'email' (Optional[str])
        'password' str

    note that either email or phoneNumber MUST be provided.
    """

    serializer = s.SignUpRequest(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save()
    return Response({"message": "Done"}, status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    """
    Login api.

    Request's body schema:
        'username' (str)
        'password' (str)
    """

    serializer = s.LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    if user := auth.login(**serializer.validated_data):
        res = Response(
            {"message": "successfully logined."}, status.HTTP_200_OK
        )
        token = auth.generate_jwt_token(user, au.generate_expire_date())
        res.set_cookie(
            "token", token, httponly=True, samesite="strict", secure=True
        )
        return res
    return Response(
        {"error": "login failed.", "code": "invalidCredentials"},
        status.HTTP_404_NOT_FOUND,
    )


@api_view(["GET"])
def logout(request):
    res = HttpResponseRedirect(reverse("user:login"))
    res.delete_cookie("token")
    return res


@api_view(["GET"])
@authenticate
def dashboard(request):
    """
    This api will return personnal informations about the
    request's user.

    User have to authenticate before reaching this endpoint.
    """

    serializer = s.UserDataSerializer(request.user)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(["POST", "DELETE"])
@authenticate
def follow(request, user_id):
    """
    Responsible for follow and unfollowing users.
    User's must profile their target user id in path parameters.

    Use 'POST' for follow and 'DELETE' for unfollow.
    """

    if request.method == "POST":
        validator = core.Follow(user_id, request.user)
        if not validator.is_valid():
            return Response(validator.errors, status.HTTP_400_BAD_REQUEST)

        validator.follow_user()
        msg = (
            "successfully created follow request."
            if validator._is_user_private
            else "successfully followed"
        )
        return Response({"message": msg}, status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        validator = core.UnFollow(user_id, request.user)
        if not validator.is_valid():
            return Response(validator.errors, status.HTTP_400_BAD_REQUEST)

        validator.unfollow_user()
        msg = (
            "successfully removed follow request."
            if validator._is_user_private
            else "successfully unfollowed."
        )
        return Response({"message": msg}, status.HTTP_200_OK)


@api_view(["PATCH"])
@authenticate
def edit_profile(request):
    """
    Responsible for editing user's profile data.
    You can find allowed fields in 'UserDataSerializer'.

    New data will passes the same validations in sign up.
    """

    serializer = s.UserDataSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.update(request.user, serializer.validated_data)
        return Response(
            {"message": "successfully changed profile data."},
            status.HTTP_200_OK,
        )
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["POST", "DELETE"])
@authenticate
def close_friend(request, user_id):
    """
    Single close friend add and remove.
    Target user must follow request user in order to become a close friend.

    Use 'POST' for follow and 'DELETE' for unfollow.
    """

    if request.method == "POST":
        validator = core.AddCloseFriend(request.user, user_id)
        if not validator.is_valid():
            return Response(validator.errors, status.HTTP_400_BAD_REQUEST)

        validator.add_close_friend()
        return Response(
            {"message": "successfully added user to your close friends list."},
            status.HTTP_201_CREATED,
        )

    else:
        validator = core.RemoveCloseFriend(request.user, user_id)
        if not validator.is_valid():
            return Response(validator.errors, status.HTTP_400_BAD_REQUEST)

        validator.remove_close_friend()
        return Response(
            {
                "message": "successfully removed user"
                " from your close friends list."
            },
            status.HTTP_200_OK,
        )


@api_view(["PATCH"])
@authenticate
def settings(request):
    """
    Users can change their settings data from this endpoint.
    You can find all allowed fields for change in 'UserSettingsSerializer'.

    Changing password and username will result in reseting user's salt.
    """

    serializer = s.UserSettingsSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    validator = core.ChangeSettings(request.user, serializer.validated_data)
    if not validator.is_valid():
        return Response(validator.errors, status.HTTP_400_BAD_REQUEST)

    validator.change_settings()
    res = Response(
        {"message": "settings updated successfully."}, status.HTTP_200_OK
    )
    if validator.revoke_token_required:
        res.set_cookie(
            "token",
            auth.generate_jwt_token(request.user, au.generate_expire_date()),
            httponly=True,
            samesite="strict",
            secure=True,
        )

    return res


@api_view(["GET"])
@authenticate
def timeline(request):
    timeline_core = core.Timeline(request.user)
    posts = timeline_core.fetch_posts()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(["GET"])
@authenticate
def get_user_data(request, username):
    user = get_object_or_404(User, username=username)

    if not request.user.can_view(user):
        serializer = s.UserPreviewSerializer(user)
        return Response(serializer.data)

    page = request.query_params.get("page")
    if page is None or not page.isdigit():
        page = 1

    posts = pm.Post.objects.filter(user=user)
    paginator = Paginator(posts, 2)
    try:
        objs = paginator.page(int(page))
    except EmptyPage:
        return Response({"error": "emptyPage"}, status.HTTP_404_NOT_FOUND)

    user.posts = objs

    serializer = s.UserPreviewSerializer(user).data

    # if int(page) == 3:
    #     import time
    #     time.sleep(5)
    #     return Response({}, status=302)

    return Response(serializer)


@api_view(["POST"])
def forgot_password(request):
    serializer = s.ForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": "invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.validated_data.get("username")

    if not user.email:
        return Response(
            {
                "message": "This user does not have an active email address "
                "for password recovery."
            },
            status.HTTP_412_PRECONDITION_FAILED,
        )

    send_forget_password_email.delay_on_commit(user.pk)
    return Response(
        {
            "message": "A mail containing forgot password link "
            "will send to your email address."
        },
        status.HTTP_200_OK,
    )


@api_view(["POST"])
def reset_password(request):
    serializer = s.ResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    code = serializer.validated_data.get("code")
    obj = r.hgetall(code)

    if obj is None or obj[
        b"expire_at"
    ].decode() <= datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"):
        r.delete(code)
        return Response(
            {"error": "Forgot password link has been expired."},
            status.HTTP_403_FORBIDDEN,
        )

    user = m.User.objects.filter(
        username=obj[b"username"].decode(), is_deleted=False
    ).first()
    user.password = serializer.validated_data["password"]
    user.save(change_salt=True)
    r.delete(code)

    return Response({"message": "Your password changed successfully."})
