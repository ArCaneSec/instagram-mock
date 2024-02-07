import datetime
from typing import Optional
from django.conf import settings

import jwt

from . import models as m
from . import utils


def login(username: str, password: str) -> Optional[m.User]:
    try:
        user = m.User.objects.get(username=username)
    except m.User.DoesNotExist:
        return None

    if user.password == utils.make_password(password, user.salt):
        return user
    return None


def generate_jwt_token(user: m.User, expire_date: datetime.datetime) -> str:
    return jwt.encode({
        "exp": expire_date,
        "username": user.username,
    }, key=settings.SECRET_KEY)
