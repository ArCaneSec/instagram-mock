from http.cookies import SimpleCookie

from django.urls import reverse
from rest_framework.test import APITestCase

from post import models as m
from user.authenticate import generate_jwt_for_test_user
from user.models import User


class TestPostCreation(APITestCase):
    def setUp(self) -> None:
        self.user = User._create_test_user("test")
        self.another_user = User._create_test_user("test2")
        self.client.cookies = SimpleCookie(
            {"token": generate_jwt_for_test_user(self.user)}
        )
        self.file = m.PostFile._create_test_file(self.user)
        self.url = reverse("post:upload")
        self.launch = lambda data: (
            self.client.post(
                self.url,
                data=data,
                format="json",
            )
        )

    def test_regular_creation(self) -> None:
        data = {
            "tags": [self.user, self.another_user],
            "caption": "test caption",
            "files": self.file,
        }
        self.launch(data)

    def test_duplicate_tag(self) -> None:
        pass

    def test_duplicate_file(self) -> None:
        pass

    def test_invalid_tag(self) -> None:
        pass

    def test_inactive_tag(self) -> None:
        pass

    def test_invalid_file(self) -> None:
        pass

    def test_inactive_file(self) -> None:
        pass
