import json
from abc import ABC
from dataclasses import dataclass, field
from typing import Callable

from user import models as u

from . import models as m


class JsonSerializableValueError(Exception):
    def __init__(self, data: dict):
        self.data = data
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
            self._error_message = e.data
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
                "code": "alreadyLiked",
            })

    def like_post(self):
        self._check_validation_passed()
        m.PostLikes.objects.create(user=self.user, post=self._post_obj)


@dataclass
class LikePostDelete(LikePost):
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

    def delete_like(self):
        self._check_validation_passed()
        self._post_like_obj.delete()
