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


