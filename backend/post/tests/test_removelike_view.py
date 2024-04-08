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
        self.launch = lambda path: self.client.delete(
            path, content_type="json"
        )

    def test_regular_remove(self):
        path = self.url(self.post.pk)
        self.launch(path)
        

    def test_invalid_post(self):
        pass

    def test_inactive_post(self):
        pass

    def test_duplicate_remove(self):
        pass
