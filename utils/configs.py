from dataclasses import dataclass

from django.conf import settings


@dataclass
class _JWT_CONFIG:
    alg: str = "HS256"
    secret: str = settings.SECRET_KEY
    expire_day_duration: int = 14
