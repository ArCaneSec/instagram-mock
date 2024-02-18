from django.http.response import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import authenticate as auth
from . import core
from . import serializers as s
from . import utils as u
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
        token = auth.generate_jwt_token(user, u.generate_expire_date())
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
