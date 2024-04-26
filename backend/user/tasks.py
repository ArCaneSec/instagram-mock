from celery import shared_task
from . import models as m


@shared_task
def send_forget_password_email(user: m.User) -> None:
    ...