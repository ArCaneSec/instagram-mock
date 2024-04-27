import datetime
from hashlib import sha256
from random import randint

import redis
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from user.models import User

from . import models as m

r = redis.Redis(settings.REDIS_BACKEND_HOST, settings.REDIS_BACKEND_PORT)


@shared_task
def send_forget_password_email(user_id: m.User) -> int:
    user = User.objects.get(pk=user_id)

    code = f"{user.username}"
    f"{datetime.datetime.now().strftime('%Y/%m/%d, %H:%M:%S')}"
    f"{randint(1000, 9999)}"
    secret = sha256(code.encode()).hexdigest()

    expire_at = (
        datetime.datetime.now() + datetime.timedelta(minutes=10)
    ).strftime("%Y/%m/%d, %H:%M:%S")

    r.hset(secret, mapping={"username": user.username, "expire_at": expire_at})

    return send_mail(
        subject="Password reset",
        message=f"Hello {user.username}, a password reset request has been "
        "initiated for your account, if this wasn't initiated by you, you can"
        f" freely ignore it.\n your code: {secret}",
        from_email="noreplay@instagram.com",
        recipient_list=[user.email],
    )
