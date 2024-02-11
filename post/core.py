import datetime
from abc import ABC
from dataclasses import dataclass, field
from typing import Callable

from rest_framework.serializers import FileField

from user import models as u

from . import models as m


class JsonSerializableValueError(Exception):
    def __init__(self, message: dict):
        self.message = message
        super().__init__()


@dataclass
class LikePost(ABC):
    user: u.User
    post_id: int
    _validation_passed: bool = field(init=False, repr=False, default=False)
    _error_message: str = field(init=False, repr=False)
    _post_obj: m.Post = field(init=False, repr=False)

    def is_valid(self, custom_validators: list[Callable]):
        try:
            self._validate_post()
            [func() for func in custom_validators]

        except JsonSerializableValueError as e:
            self._error_message = e.message
            return False

        self._validation_passed = True
        return True

    def _validate_post(self):
        post = m.Post.objects.filter(pk=self.post_id, is_active=True).first()
        if not post:
            raise JsonSerializableValueError(
                {"error": "post not found.", "code": "invalidPost"}
            )
        self._post_obj = post

    def _check_validation_passed(self):
        if not self._validation_passed:
            raise JsonSerializableValueError(
                "You cannot call this function without "
                "running validations first."
            )

    @property
    def errors(self):
        return self._error_message


@dataclass
class LikePostCreate(LikePost):

    def is_valid(self):
        return super().is_valid([self._check_user_havent_liked])

    def _check_user_havent_liked(self):
        user_liked = m.PostLikes.objects.filter(
            user=self.user, post=self._post_obj
        ).first()
        if user_liked:
            raise JsonSerializableValueError({
                "error": "you have already liked this post.",
                "code": "duplicateLike",
            })

    def like_post(self):
        self._check_validation_passed()
        m.PostLikes.objects.create(user=self.user, post=self._post_obj)


@dataclass
class RemovePostLike(LikePost):
    _post_like_obj: m.PostLikes = field(init=False, repr=False)

    def is_valid(self):
        return super().is_valid([self._check_user_has_liked])

    def _check_user_has_liked(self):
        user_liked = m.PostLikes.objects.filter(
            user=self.user, post=self._post_obj
        ).first()
        if not user_liked:
            raise JsonSerializableValueError({
                "error": "you haven't liked this post yet.",
                "code": "notLiked",
            })
        self._post_like_obj = user_liked

    def remove_like(self):
        self._check_validation_passed()
        self._post_like_obj.delete()


@dataclass
class PostFileValidator:
    user: u.User
    capacity: int = field(default=10)
    date: datetime.date = field(default_factory=datetime.date.today)
    _error_messages: str = field(init=False, repr=False)

    def is_valid(self) -> bool:
        try:
            self._validate_date_total_uploads()
        except JsonSerializableValueError as e:
            self._error_messages = e.message
            return False

        return True

    @property
    def errors(self):
        return self._error_messages

    def _validate_date_total_uploads(self):
        today_files = m.PostFile.objects.filter(
            created_at=self.date, post__isnull=True
        )
        if len(today_files) >= self.capacity:
            raise JsonSerializableValueError({
                "error": "you have reached the maximum "
                "number of files for today.",
                "code": "capacity",
            })


@dataclass
class PostFile:
    content_type: str
    content: FileField
    validator: PostFileValidator

    @staticmethod
    def delete_today_files(date: datetime.date) -> None:
        m.PostFile.objects.filter(created_at=date, post__isnull=True).delete()

    def upload_file(self) -> int:
        if not self.validator.is_valid():
            raise ValueError(
                "You cannot call this method without validating data."
            )

        return m.PostFile.objects.create(
            user=self.validator.user,
            content_type=self.content_type,
            content=self.content,
        ).pk
