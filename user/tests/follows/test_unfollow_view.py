from utils.utils_tests import ViewTests

from .test_follow_views import _check_follower_request
from .test_unfollow import _follow_user

PATH = "user:follow"


class UnfollowViewTest(ViewTests):
    def setUp(self) -> None:
        self.user = self.create_user("test")
        self.anoter_user = self.create_user("another_user")
        self.set_cookie("token", self.user)
        _follow_user(self.user, self.anoter_user)

    def test_regular_unfollow(self) -> None:
        self.create_url(PATH, [self.anoter_user.pk])
        res = self.launch_delete()
        self.assertEqual(res.status_code, 200, res.json())
        self.assertEqual(self.anoter_user.total_followers, 0)
        self.assertEqual(self.user.total_followings, 0)

    def test_invalid_unfollow(self) -> None:
        self.create_url(PATH, [85])
        res = self.launch_delete()
        self.assertEqual(res.status_code, 400, res.json())

    def test_duplicate_unfollow(self) -> None:
        self.create_url(PATH, [self.anoter_user.pk])
        res = self.launch_delete()
        res = self.launch_delete()
        self.assertEqual(res.status_code, 400, res.json())

    def test_notfollowed_user_unfollow(self):
        test_user = self.create_user("test_user")
        self.create_url(PATH, [test_user.pk])
        res = self.launch_delete()
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(self.user.total_followings, 1)

    def test_remove_follow_request(self):
        self.anoter_user.follow_requests.remove(self.user)
        self.anoter_user.is_private = True
        self.anoter_user.save()
        self.anoter_user.follow_requests.add(self.user)
        self.assertEqual(
            _check_follower_request(self.user, self.anoter_user), True
        )

        self.create_url(PATH, [self.anoter_user.pk])
        res = self.launch_delete()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.anoter_user.follow_requests.count(), 0)
