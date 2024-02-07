from . import models as m


def validate_username(username: str):
    return not bool(m.User.objects.filter(username=username).first())


def validate_email(email: str):
    return not bool(m.User.objects.filter(email=email).first())


def validate_phone(phone_number: str):
    return not bool(m.User.objects.filter(phone_number=phone_number).first())
