from rest_framework.test import APITestCase

from user.core import Follow
from user.models import User

from .test_follow_views import (
    _check_follower,
    _check_follower_request,
    _check_following,
    _check_following_request,
)


class TestFollow(APITestCase):
    def setUp(self):
        self.user = User._create_test_user("test", False)
        self.target_user = User._create_test_user("another_test", False)

    def test_regular_follow(self):
        validator = Follow(self.target_user.pk, self.user)
        self.assertEqual(validator.is_valid(), True)
        validator.follow_user()
        self.assertEqual(_check_follower(self.user, self.target_user), True)
        self.assertEqual(_check_following(self.user, self.target_user), True)

    def test_self_follow(self):
        validator = Follow(self.user.pk, self.user)
        self.assertEqual(validator.is_valid(), False)
        self.assertRaises(PermissionError, validator.follow_user)
        self.assertEqual(_check_follower(self.user, self.target_user), False)
        self.assertEqual(_check_following(self.user, self.target_user), False)

    def test_duplicate_follow(self):
        validator = Follow(self.target_user.pk, self.user)
        validator.is_valid() and validator.follow_user()
        self.assertRaises(PermissionError, validator.follow_user)
        self.assertEqual(self.target_user.total_followers, 1)
        self.assertEqual(self.user.total_followings, 1)

    def test_invalid_follow(self):
        validator = Follow(85, self.user)
        self.assertEqual(validator.is_valid(), False)
        self.assertRaises(PermissionError, validator.follow_user)

    def test_private_follow(self):
        self.target_user.is_private = True
        self.target_user.save()
        validator = Follow(self.target_user.pk, self.user)
        self.assertEqual(validator.is_valid(), True)
        validator.follow_user()
        self.assertEqual(
            _check_follower_request(self.user, self.target_user), True
        )
        self.assertEqual(
            _check_following_request(self.user, self.target_user), True
        )
