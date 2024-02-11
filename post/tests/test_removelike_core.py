from rest_framework.test import APITestCase

from post import core as c
from post import models as m
from user.models import User


class TestRemovePostLike(APITestCase):
    def setUp(self):
        self.user = User._create_test_user("test")
        self.post = m.Post._create_test_post(self.user, True)
        m.PostLikes.objects.create(user=self.user, post=self.post)
        self.post_is_liked = lambda: bool(
            m.PostLikes.objects.filter(user=self.user, post=self.post).first()
        )
        self.assertEqual(
            self.post_is_liked(),
            True,
            "post was not liked before testing the like removal",
        )

    def test_regular_remove(self) -> None:
        remove_post_process = c.RemovePostLike(self.user, self.post.pk)
        remove_post_process.is_valid() and remove_post_process.remove_like()
        self.assertEqual(self.post_is_liked(), False)

    def test_invalid_post(self) -> None:
        remove_post_process = c.RemovePostLike(self.user, 2)
        self.assertEqual(remove_post_process.is_valid(), False)

    def test_inactive_post(self) -> None:
        post = m.Post._create_test_post(self.user, False)
        remove_post_process = c.RemovePostLike(self.user, post.pk)
        self.assertEqual(remove_post_process.is_valid(), False)

    def test_duplicate_remove(self) -> None:
        remove_post_process = c.RemovePostLike(self.user, self.post.pk)
        remove_post_process.is_valid() and remove_post_process.remove_like()
        remove_post_process = c.RemovePostLike(self.user, self.post.pk)
        self.assertEqual(remove_post_process.is_valid(), False)
