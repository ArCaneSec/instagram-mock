from django.contrib.auth.hashers import make_password
from django.db import models as m

from . import utils

# Create your models here.


class BasicUserInfo(m.Model):
    username = m.CharField(max_length=250, unique=True)
    nickname = m.CharField(max_length=250, blank=True, default=username)
    first_name = m.CharField(max_length=250)
    last_name = m.CharField(max_length=250)
    profile = m.ImageField(
        upload_to="static/users/profiles/", null=True, blank=True
    )
    biography = m.TextField(null=True, blank=True)
    email = m.EmailField(null=True, blank=True, unique=True)
    phone_number = m.CharField(
        max_length=11, null=True, blank=True, unique=True
    )
    is_active = m.BooleanField(default=False)
    is_deleted = m.BooleanField(default=False)

    class Meta:
        abstract = True


class User(BasicUserInfo):
    is_private = m.BooleanField(default=False)
    password = m.CharField(max_length=128)
    salt = m.CharField(default=utils.generate_hash, max_length=100)
    followers = m.ManyToManyField(
        to="self",
        through="Follows",
        related_name="followings",
        symmetrical=False,
    )
    close_friends = m.ManyToManyField(
        to="self", symmetrical=False, related_name="followings_close_friends"
    )
    hide_story = m.ManyToManyField(
        to="self", symmetrical=False, related_name="followings_hide_story"
    )

    def __str__(self) -> str:
        return "%s %s %s" % (
            super().username,
            super().first_name,
            super().last_name,
        )

    def save(self, *args, **kwargs):
        self.password = make_password(self.password, self.salt)
        super().save(*args, **kwargs)


class Follows(m.Model):
    following = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="followed_user"
    )
    follower = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="following_user"
    )
    date = m.DateTimeField(auto_now_add=True)
