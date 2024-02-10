from http.cookies import SimpleCookie

from rest_framework.test import APITestCase

from post import core as c
from post import models as m
from user.models import User


class TestPostLikes(APITestCase):
    def setUp(self):
        self.user = User._create_test_user("test")
        self.post = m.Post._create_test_post(self.user, True)
        self.post_is_liked = lambda: bool(
            m.PostLikes.objects.filter(user=self.user, post=self.post).first()
        )

    def test_valid_data(self):
        like_post = c.LikePostCreate(self.user, 1)
        like_post.is_valid() and like_post.like_post()

        self.assertEqual(self.post_is_liked(), True)

    def test_invalid_post(self):
        like_post = c.LikePostCreate(self.user, 2)
        self.assertEqual(
            like_post.is_valid(),
            False,
            "is_valid is true with invalid post id",
        )

    def test_inactive_post(self):
        post = m.Post._create_test_post(self.user, is_active=False)
        like_post = c.LikePostCreate(self.user, post.pk)
        self.assertEqual(
            like_post.is_valid(), False, "is_valid is true with inactive post"
        )
