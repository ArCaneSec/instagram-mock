from rest_framework.test import APITestCase

from user.core import UnFollow
from user.models import User

from .test_follow_views import (
    _check_follower,
    _check_follower_request,
    _check_following_request,
)


def _follow_user(from_user: User, to_user: User):
    to_user.followers.add(from_user)


class TestUnFollow(APITestCase):
    def setUp(self):
        self.user = User._create_test_user("test", False)
        self.target_user = User._create_test_user("another_test", False)
        _follow_user(self.user, self.target_user)

    def test_regular_unfollow(self):
        self.assertEqual(self.target_user.total_followers, 1)
        validator = UnFollow(self.target_user.pk, self.user)
        self.assertEqual(validator.is_valid(), True)
        validator.unfollow_user()
        self.assertEqual(_check_follower(self.user, self.target_user), False)
        self.assertEqual(self.target_user.total_followers, 0)

    def test_self_unfollow(self):
        validator = UnFollow(self.user.pk, self.user)
        self.assertEqual(validator.is_valid(), False)
        self.assertRaises(PermissionError, validator.unfollow_user)

    def test_notfollowed_unfollow(self):
        random_user = User._create_test_user("random")
        random_user.followings.add(self.target_user)

        self.target_user.followers.remove(self.user.pk)

        validator = UnFollow(self.target_user.pk, self.user)
        self.assertEqual(validator.is_valid(), False)
        self.assertEqual(self.target_user.total_followers, 1)

    def test_remove_follow_request(self):
        self.target_user.is_private = True
        self.target_user.save()

        self.target_user.followers.remove(self.user)
        self.target_user.follow_requests.add(self.user)
        self.assertEqual(
            _check_follower_request(self.user, self.target_user), True
        )

        validator = UnFollow(self.target_user.pk, self.user)
        self.assertEqual(validator.is_valid(), True)

        validator.unfollow_user()
        self.assertEqual(
            _check_follower_request(self.user, self.target_user), False
        )
        self.assertEqual(
            _check_following_request(self.user, self.target_user), False
        )
