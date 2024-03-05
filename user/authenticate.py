import datetime
from functools import wraps
from typing import Callable, Optional

import jwt
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from utils import auth_utils as utils
from utils.configs import _JWT_CONFIG

from . import models as m


def generate_jwt_for_test_user(user: m.User) -> str:
    return generate_jwt_token(user, utils.generate_expire_date())


def login(username: str, password: str) -> Optional[m.User]:
    try:
        user = m.User.objects.get(username=username, is_active=True)
    except m.User.DoesNotExist:
        return None

    if user.password == utils.make_password(password, user.salt):
        return user
    return None


def generate_jwt_token(user: m.User, expire_date: datetime.datetime) -> str:
    return jwt.encode(
        {"username": user.username, "exp": expire_date, "salt": user.salt},
        key=_JWT_CONFIG.secret,
        algorithm=_JWT_CONFIG.alg,
    )


def authenticate(func: Callable):
    @wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        token = request.COOKIES.get("token")
        if not token:
            return HttpResponseRedirect(redirect_to=reverse("user:login"))
        decoded_token, invalid_response = _validate_jwt_token(token)
        if not decoded_token:
            return invalid_response

        if not (user := _get_user_from_jwt_token(decoded_token)):
            return Response(
                {"error": "user not found.", "code": "notFound"},
                status.HTTP_404_NOT_FOUND,
            )

        request.user = user
        return func(request, *args, **kwargs)

    return wrapper


def _validate_jwt_token(
    token: str,
) -> tuple[Optional[HttpResponse], Optional[dict]]:
    try:
        decoded_token = jwt.decode(
            token, _JWT_CONFIG.secret, algorithms=_JWT_CONFIG.alg
        )
    except (jwt.DecodeError, jwt.InvalidSignatureError):
        return None, Response(
            {"error": "Invalid signature.", "code": "forbidden"},
            status.HTTP_403_FORBIDDEN,
        )
    except jwt.ExpiredSignatureError:
        return None, HttpResponseRedirect(
            redirect_to=reverse("user:login"), content_type="application/json"
        )

    return decoded_token, None


def _get_user_from_jwt_token(decoded_token: dict) -> Optional[m.User]:
    username = decoded_token["username"]
    salt = decoded_token["salt"]
    return m.User.objects.filter(
        username=username, salt=salt, is_active=True
    ).first()
