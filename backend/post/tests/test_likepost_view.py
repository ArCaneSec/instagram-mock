from http.cookies import SimpleCookie

from django.urls import reverse
from rest_framework.test import APITestCase

from post import models as m
from user.authenticate import generate_jwt_for_test_user
from user.models import User


class TestPostLikes(APITestCase):
    def setUp(self) -> None:
        self.user = User._create_test_user("test")
        self.post = m.Post._create_test_post(self.user, is_active=True)
        self.client.cookies = SimpleCookie(
            {"token": generate_jwt_for_test_user(self.user)}
        )
        self.url = lambda post_id: reverse("post:like", args=[post_id])
        self.launch = lambda path: self.client.put(path)

    def test_regular_like_req(self) -> None:
        path = self.url(self.post.pk)
        res = self.launch(path)
        self.assertEqual(res.status_code, 201)

    def test_duplicate_req(self) -> None:
        path = self.url(self.post.pk)
        _ = self.launch(path)
        res = self.launch(path)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], "duplicateLike")

    def test_invalid_post_req(self) -> None:
        path = self.url(2)
        res = self.launch(path)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], "invalidPost")

    def test_inactive_post_req(self) -> None:
        post = m.Post._create_test_post(self.user, is_active=False)
        path = self.url(post.pk)
        res = self.launch(path)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], "invalidPost")
