from dataclasses import dataclass, field
from typing import Callable

from post.core import JsonSerializableValueError
from utils.validators import Validator, validation_required

from . import models as m


@dataclass
class Follows(Validator):
    user_id: int
    from_user: m.User
    _user_obj: m.User = field(repr=False, init=False)

    def is_valid(self, custom_validators: list[Callable] = []):
        try:
            self._validate_user()
            [validator() for validator in custom_validators]
        except JsonSerializableValueError as e:
            self._error = e
            return False

        self._validation_passed = True
        return True

    def _validate_user(self):
        valid_user = (
            m.User.objects.filter(pk=self.user_id, is_active=True)
            .exclude(pk=self.from_user.pk)
            .first()
        )
        if not valid_user:
            raise JsonSerializableValueError(
                {"error": "user not found.", "code": "userNotFound"}
            )

        self._user_obj = valid_user
        return

    @property
    def _is_user_private(self) -> bool:
        return self._user_obj.is_private


@dataclass
class Follow(Follows):

    def is_valid(self) -> bool:
        return super().is_valid([self._check_user_isnt_already_following])

    def _check_user_isnt_already_following(self):
        if self._user_obj.followers.filter(pk=self.from_user.pk).first():
            raise JsonSerializableValueError(
                {
                    "error": "user is already being followed",
                    "code": "duplicateFollow",
                }
            )

    @validation_required
    def follow_user(self):
        if self._is_user_private:
            self._user_obj.follow_requests.add(self.from_user)
            return

        self._user_obj.followers.add(self.from_user)


class UnFollow(Follows):
    def is_valid(self) -> bool:
        return super().is_valid([self._check_user_is_already_following])

    def _check_user_is_already_following(self):
        if self._user_obj.followers.filter(
            pk=self.from_user.pk
        ).first():
            return

        if not self._user_obj.follow_requests.filter(
            pk=self.from_user.pk
        ).first():
            raise JsonSerializableValueError(
                {
                    "error": "user is not being followed",
                    "code": "notFollowing",
                }
            )

    @validation_required
    def unfollow_user(self):
        if self._is_user_private:
            self._user_obj.follow_requests.remove(self.from_user)
            return

        self._user_obj.followers.remove(self.from_user)
