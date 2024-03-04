import re

from django.db import models as m
from rest_framework.serializers import ValidationError

from utils import auth_utils as utils

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
    salt = m.CharField(max_length=100)
    followers = m.ManyToManyField(
        to="self",
        through="Follow",
        symmetrical=False,
        related_name="followings",
        blank=True,
    )
    follow_requests = m.ManyToManyField(
        to="self",
        through="FollowRequest",
        symmetrical=False,
        related_name="followings_follow_requests",
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

    @property
    def total_follow_requests(self):
        return self.follow_requests.count()

    def save(self, *args, **kwargs):
        if kwargs.pop("change_salt", None):
            self.salt = utils.generate_hash()
            self.password = utils.make_password(self.password, self.salt)

        if not self.nickname:
            self.nickname = self.username

        if not (self.email or self.phone_number):
            raise ValueError(
                "You have to provide an email address or phone number "
                "in order to sign up."
            )

        super().save(*args, **kwargs)

    @staticmethod
    def is_username_duplicate(username: str) -> bool:
        return bool(
            User.objects.filter(username=username, is_deleted=False).first()
        )

    @staticmethod
    def validate_username(username: str):
        pattern = r"[a-z][a-z\d._]{2,250}$"
        if not re.match(pattern, username):
            raise ValidationError(
                {
                    "error": "username is not valid, it must contains "
                    "between 3, 250 characters, start with absolute character,"
                    "and must not contains special characters like @#$...",
                    "code": "invalidUser",
                }
            )

        if User.objects.filter(username=username, is_deleted=False):
            raise ValidationError(
                {
                    "error": "username is not unique.",
                    "code": "nonUniqueUserName",
                }
            )

    def validate_phone_number(phone_number: str):
        if not phone_number.isdigit():
            raise ValidationError(
                {
                    "error": "phoneNumber must be digit only.",
                    "code": "nonDigitNumber",
                }
            )
        if User.objects.filter(phone_number=phone_number, is_deleted=False):
            raise ValidationError(
                {
                    "error": "phoneNumber is not unique",
                    "code": "nonUniquePhoneNumber",
                }
            )
        if len(phone_number) != 11:
            raise ValidationError(
                {"error": "phone number is not valid.", "code": "invalidValue"}
            )

    @staticmethod
    def validate_email(email: str):
        if User.objects.filter(email=email, is_deleted=False):
            raise ValidationError(
                {"error": "email is not unique.", "code": "nonUniqueEmail"}
            )

    @staticmethod
    def validate_password(password: str):
        """
        Checking if password is strong enough.

        Args:
            'password' (str)
        """

        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$"
        if not re.match(pattern, password):
            raise ValidationError(
                {
                    "error": "Password must contain atleast 8 characters,"
                    " 1 one lowercase and 1 uppercase letter and 1 digit.",
                    "code": "weakPassword",
                }
            )

    @staticmethod
    def _create_test_user(username: str, is_private: bool = False) -> "User":
        return User.objects.create(
            username=username,
            nickname="%s nickname" % username,
            first_name="%s first_name" % username,
            last_name="%s last_name" % username,
            email="%s@%s.com" % (username, username),
            phone_number=username if len(username) < 12 else username[0:12],
            password=username,
            is_private=is_private,
        )

    def __str__(self) -> str:
        return "%s %s %s" % (
            super().username,
            super().first_name,
            super().last_name,
        )


class Follow(m.Model):
    following = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="user_followers"
    )
    follower = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="user_followings"
    )
    date = m.DateTimeField(auto_now_add=True)


class FollowRequest(m.Model):
    to_user = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="incoming_follow_requets"
    )
    from_user = m.ForeignKey(
        User, on_delete=m.CASCADE, related_name="pending_follow_requests"
    )
    created_at = m.DateTimeField(auto_now_add=True)
