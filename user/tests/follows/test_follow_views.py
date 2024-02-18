from user.models import User
from utils.utils_tests import ViewTests


def _check_follower(user: User, target_user: User) -> bool:
    return bool(target_user.followers.filter(pk=user.pk).first())


def _check_following(user: User, target_user: User) -> bool:
    return bool(user.followings.filter(pk=target_user.pk).first())


def _check_follower_request(user: User, target_user: User) -> bool:
    return bool(target_user.follow_requests.filter(pk=user.pk).first())


def _check_following_request(user: User, target_user: User) -> bool:
    return bool(
        user.followings_follow_requests.filter(pk=target_user.pk).first()
    )


class TestFollow(ViewTests):
    def setUp(self):
        self.user = self.create_user("test", True)
        self.set_cookie("token", self.user)

    def _check_follower(self, user: User, target_user: User) -> bool:
        return bool(target_user.followers.filter(pk=user.pk).first())

    def test_regular_follow(self):
        target_user = self.create_user("another_user", False)
        self.create_url("user:follow", [target_user.pk])
        res = self.launch_post()
        self.assertEqual(res.status_code, 201, res.json())
        self.assertEqual(_check_follower(self.user, target_user), True)
        self.assertEqual(_check_following(self.user, target_user), True)

    def test_self_follow(self):
        self.create_url("user:follow", [self.user.pk])
        res = self.launch_post()
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(_check_follower(self.user, self.user), False)
        self.assertEqual(_check_following(self.user, self.user), False)

    def test_private_follow(self):
        target_user = self.create_user("another_user", True)
        self.create_url("user:follow", [target_user.pk])
        res = self.launch_post()
        self.assertEqual(res.status_code, 201, res.json())
        self.assertEqual(_check_follower_request(self.user, target_user), True)
        self.assertEqual(
            _check_following_request(self.user, target_user), True
        )

    def test_invalid_user(self):
        self.create_url("user:follow", [85])
        res = self.launch_post()
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(self.user.total_followings, 0)

    def test_inactive_user(self):
        target_user = self.create_user("another_user")
        target_user.is_active = False
        target_user.save()
        self.create_url("user:follow", [target_user.pk])
        res = self.launch_post()
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(self.user.total_followers, 0)
        self.assertEqual(target_user.total_followers, 0)

    def test_duplicate_follow(self):
        target_user = self.create_user("another_user")
        self.create_url("user:follow", [target_user.pk])
        res = self.launch_post()
        res = self.launch_post()
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(
            res.json()["code"],
            "duplicateFollow",
            res.json(),
        )
        self.assertEqual(target_user.total_followers, 1)
