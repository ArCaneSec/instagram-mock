import re

from django.db.models import Q

from . import models as m


def validate_uniqueness(username: str, email: str, phone_number: str) -> bool:
    return not bool(
        m.User.objects.filter(
            Q(username=username)
            | Q(email=email)
            | Q(phone_number=phone_number)
        )
    )


def validate_password(password: str) -> bool:
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,}$"
    return bool(re.match(pattern, password))
