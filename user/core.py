import datetime
from dataclasses import dataclass, field
from typing import Callable

from django.db.models import QuerySet

from post import models as pm
from post.core import JsonSerializableValueError
from utils.auth_utils import make_password
from utils.decorators import validation_required
from utils.validators import Validator

from . import models as m


@dataclass
class Follows(Validator):
    """
    Base class for follow/unfollow's logic classes.
    Here we will check if the target user is valid and active,
    then run other validators for child classes.

    Attributes:
        user_id: Target user's id.
        from_user: The request user.
        _user_obj: Target user's 'User' object.
    """

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
        if self._user_obj.followers.filter(pk=self.from_user.pk).first():
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


@dataclass
class CloseFriend(Validator):
    request_user: m.User
    target_user_id: int
    _target_user: m.User = field(init=False, repr=False)

    def _fetch_target_user(self):
        self._target_user = (
            m.User.objects.filter(pk=self.target_user_id, is_active=True)
            .exclude(pk=self.request_user.pk)
            .first()
        )
        if not self._target_user:
            raise JsonSerializableValueError(
                {"error": "invalid user", "code": "invalidUser"}
            )

    def _is_user_following_target(self):
        if not self._target_user.followers.filter(pk=self.request_user.pk):
            raise JsonSerializableValueError(
                {
                    "error": "user is not following you at the moment.",
                    "code": "userNotFollowing",
                }
            )

    def is_valid(self, custom_validators: list[Callable] = []):
        try:
            self._fetch_target_user()
            self._is_user_following_target()
            self._fetch_target_user()
            [validator() for validator in custom_validators]
        except JsonSerializableValueError as e:
            self._error = e
            return False

        self._validation_passed = True
        return True


@dataclass
class AddCloseFriend(CloseFriend):
    def is_valid(self):
        return super().is_valid([self._check_user_not_in_cf_already])

    def _check_user_not_in_cf_already(self):
        if self.request_user.close_friends.filter(pk=self._target_user.pk):
            raise JsonSerializableValueError(
                {
                    "error": "user is already in your close friends list.",
                    "code": "duplicateCloseFriend",
                }
            )

    @validation_required
    def add_close_friend(self):
        self.request_user.close_friends.add(self._target_user)


class RemoveCloseFriend(CloseFriend):
    def is_valid(self):
        return super().is_valid([self._check_user_is_in_cf_already])

    def _check_user_is_in_cf_already(self):
        if not self.request_user.close_friends.filter(pk=self._target_user.pk):
            raise JsonSerializableValueError(
                {
                    "error": "user is not in your close friends list..",
                    "code": "notCloseFriend",
                }
            )

    @validation_required
    def remove_close_friend(self):
        self.request_user.close_friends.remove(self._target_user)


@dataclass
class ChangeSettings(Validator):
    user: m.User
    data: dict
    revoke_token_required: bool = field(default=False, init=False)
    _change_salt: bool = field(default=False, init=False)

    def is_valid(self) -> bool:
        try:
            self._validate_password()
            self._validate_username()
            self._validate_privacy_change()
        except JsonSerializableValueError as e:
            self._error = e
            return False

        self._validation_passed = True
        return True

    def _validate_password(self) -> bool:
        if not (password := self.data.get("password")):
            return

        self.revoke_token_required = True

        if make_password(password, self.user.salt) != self.user.password:
            raise JsonSerializableValueError(
                {
                    "error": "password is invalid.",
                    "code": "invalidPassword",
                }
            )
        self._change_salt = True

        if new_password := self.data.pop("new_password", None):
            self.data["password"] = new_password

    def _validate_username(self):
        if not (username := self.data.get("username")):
            return

        if m.User.is_username_duplicate(username):
            raise JsonSerializableValueError(
                {
                    "error": "username already exists.",
                    "code": "duplicateUsername",
                }
            )

    def _validate_privacy_change(self):
        privacy = self.data.get("is_private")
        if privacy is None:
            return

        if self.user.is_private == privacy:
            raise JsonSerializableValueError(
                {
                    "error": "your account privacy "
                    f"is already set to {privacy}.",
                    "code": "alreadyTheSame",
                }
            )
        if not privacy:
            self._accept_follow_requests = True

    @validation_required
    def change_settings(self) -> bool:
        # for key, value in self.data.items():
        #     setattr(self.user, key, value)

        # self.user.save(
        #     change_salt=self._change_salt,
        # )

        if (
            hasattr(self, "_accept_follow_requests")
            and self._accept_follow_requests
        ):
            self.user.followers.add(
                *self.user.follow_requests.all().values_list("id", flat=True)
            )
            m.FollowRequest.objects.filter(to_user=self.user.pk).delete()


@dataclass
class Timeline:
    """
    This class is responsible for filling users timeline with
    related posts.

    First we look for user's followings new uploaded posts, if
    user already seen those posts, then we look for related posts
    that exists in their liked hashatgs.
    """

    request_user: m.User

    def fetch_posts(self) -> QuerySet[pm.Post]:
        followings = self._fetch_followings()
        posts = self._fetch_recent_followings_posts(followings)
        if posts.count() >= 5:
            return posts

        related_posts = self._fetch_related_posts(5 - posts.count())
        return posts | related_posts if related_posts else posts

    def _fetch_followings(self):
        """
        Fetching all user's followings.
        """

        followings = (
            m.Follow.objects.filter(follower=self.request_user)
            .all()
            .order_by("date")
            .select_related("following")
        )
        return [follow_obj.following for follow_obj in followings]

    def _fetch_recent_followings_posts(
        self, followings: QuerySet[m.Follow]
    ) -> QuerySet[pm.Post]:
        """
        Fetching recently uploaded posts by user's followings which
        user has not seen them yet.
        """

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        two_days_ago = now - datetime.timedelta(days=2)
        posts = pm.Post.objects.filter(
            user__in=followings, created_at__range=[two_days_ago, now]
        ).exclude(viewers=self.request_user)[:5]
        pm.PostViewsHistory.objects.bulk_create(
            [
                pm.PostViewsHistory(user=self.request_user, post=post)
                for post in posts
            ]
        )
        return posts

    def _fetch_related_posts(self, max: int) -> QuerySet[pm.Post]:
        """
        Extracting user's liked post's hashtags, then fetching
        newly uploaded posts containing those hashtags.
        """

        recent_liked_posts = pm.PostLikes.fetch_recent_liked_posts(
            self.request_user
        )
        duplicate_tags = set()
        tags = set()
        posts = None

        while len(recent_liked_posts) != 0:
            for post in recent_liked_posts:
                post: pm.Post
                hashtags = (
                    post.hashtags.all()
                    .values_list("title", flat=True)
                    .exclude(title__in=duplicate_tags)
                    .distinct()
                )
                # Removing so we dont look for duplicate hashtags.
                recent_liked_posts.remove(post)
                if not hashtags:
                    continue

                tags.update(hashtags)
                if len(tags) >= 5:
                    duplicate_tags.update(tags)
                    tags = []
                    break
            query = (
                pm.Post.objects.filter(hashtags__title__in=tags)
                .exclude(viewers=self.request_user, user__is_private=False)
                .distinct()[:max]
            )

            if posts:
                posts.union(query)
            else:
                posts = query

            if not 5 > len(posts) > 0:
                break

        pm.PostViewsHistory.objects.bulk_create(
            [
                pm.PostViewsHistory(user=self.request_user, post=post)
                for post in posts
            ]
        )
        return posts
