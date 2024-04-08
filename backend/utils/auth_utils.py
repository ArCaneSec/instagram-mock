import datetime
from hashlib import sha256
from random import randint

from utils.configs import _JWT_CONFIG


def generate_hash() -> str:
    salt = map(chr, [randint(33, 129) for _ in range(1, 6)])
    return "".join(salt)


def make_password(password: str, salt: str):
    return sha256(password.encode() + salt.encode()).hexdigest()


def generate_expire_date() -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(
        days=_JWT_CONFIG.expire_day_duration
    )
