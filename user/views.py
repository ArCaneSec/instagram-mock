from django.http.response import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils import auth_utils as au

from . import authenticate as auth
from . import core
from . import serializers as s
from .authenticate import authenticate

# Create your views here.


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
