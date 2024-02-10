from typing import Optional

from django.db import models as m

from . import utils

# Create your models here.


class BasicUserInfo(m.Model):
    username = m.CharField(max_length=250, unique=True)
    nickname = m.CharField(max_length=250, blank=True)
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
    is_active = m.BooleanField(default=True)
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
        blank=True,
    )
    close_friends = m.ManyToManyField(
        to="self",
        symmetrical=False,
        related_name="followings_close_friends",
        blank=True,
    )
    hide_story = m.ManyToManyField(
        to="self",
        symmetrical=False,
        related_name="followings_hide_story",
        blank=True,
    )

    @property
    def total_followers(self):
        return self.followers.count()

    @property
    def total_followings(self):
        return self.followings.count()

    def save(self, *args, **kwargs):
        self.password = utils.make_password(self.password, self.salt)
        if not self.nickname:
            self.nickname = self.username

        super().save(*args, **kwargs)

    @staticmethod
    def login(username: str, password: str) -> Optional["User"]:
        try:
            user = User.objects.get(username=username, is_active=False)
        except User.DoesNotExist:
            return None

        if user.password == utils.make_password(password, user.salt):
            return user
        return None

    @staticmethod
    def _create_test_user(username: str) -> "User":
        return User.objects.create(
            username=username,
            nickname="%s nickname" % username,
            first_name="%s first_name" % username,
            last_name="%s last_name" % username,
            email="%s@%s.com" % (username, username),
            phone_number=username if len(username) < 12 else username[0, 12],
            password=username,
        )

    def __str__(self) -> str:
        return "%s %s %s" % (
            super().username,
            super().first_name,
            super().last_name,
        )


class Follows(m.Model):
    following = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="followed_user"
    )
    follower = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="following_user"
    )
    date = m.DateTimeField(auto_now_add=True)
