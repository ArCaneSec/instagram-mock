import datetime
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Optional

import jwt
from django.conf import settings
from django.http.response import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.urls import reverse
from rest_framework.request import Request

from . import models as m
from . import utils


@dataclass
class _JWT_CONFIG:
    alg: str = "HS256"
    secret: str = settings.SECRET_KEY


def login(username: str, password: str) -> Optional[m.User]:
    try:
        user = m.User.objects.get(username=username)
    except m.User.DoesNotExist:
        return None

    if user.password == utils.make_password(password, user.salt):
        return user
    return None


def generate_jwt_token(user: m.User, expire_date: datetime.datetime) -> str:
    return jwt.encode(
        {
            "username": user.username,
            "exp": expire_date,
        },
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
            return HttpResponseNotFound(
                {"error": "user not found.", "code": "notFound"}
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
        return None, HttpResponseForbidden(
            {"error": "Invalid signature.", "code": "unAuthorized"}
        )
    except jwt.ExpiredSignatureError:
        return None, HttpResponseRedirect(redirect_to=reverse("user:login"))

    return decoded_token, None


def _get_user_from_jwt_token(decoded_token: dict) -> Optional[m.User]:
    username = decoded_token["username"]
    return m.User.objects.filter(username=username, is_active=True).first()
