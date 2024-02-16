from abc import ABC
from dataclasses import dataclass, field
from typing import Callable

from post.core import JsonSerializableValueError

from . import models as m


@dataclass
class Follows(ABC):
    user_id: int
    from_user: m.User
    _validation_passed: bool = field(repr=False, init=False, default=False)
    _error_message: str = field(repr=False, init=False, default="")
    _user_obj: m.User = field(repr=False, init=False)

    def is_valid(self, custom_validators: list[Callable] = []):
        try:
            self._validate_user()
            [validator() for validator in custom_validators]
        except JsonSerializableValueError as e:
            self._error_messages = str(e)
            return False

        return True

    def _validate_user(self):
        valid_user = m.User.objects.filter(
            pk=self.user_id, is_active=True
        ).first()
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
        return super().is_valid(self._check_user_isnt_already_following)

    def _check_user_isnt_already_following(self):
        if self._user_obj.followers.filter(
            follower=self.from_user, following=self._user_obj
        ).first():
            raise JsonSerializableValueError(
                {
                    "error": "user is already being followed",
                    "code": "dupliacateFollow",
                }
            )

    def follow_user(self):
        if self._is_user_private:
            self._user_obj.follow_requests.add(
                from_user=self.from_user, to_user=self._user_obj
            )
            return

        self._user_obj.followers.add(self.from_user)


class RemoveFollow(Follows):
    def is_valid(self) -> bool:
        return super().is_valid(self._check_user_is_already_following)

    def _check_user_is_already_following(self):
        if not self._user_obj.followers.filter(
            follower=self.from_user, following=self._user_obj
        ).first():
            raise JsonSerializableValueError(
                {
                    "error": "user is not being followed",
                    "code": "notFollowing",
                }
            )

    def remove_follow(self):
        if self._is_user_private:
            self._user_obj.follow_requests.remove(from_user=self.from_user)
            return
        
        self._user_obj.followers.remove(self.from_user)


