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
            "tags": [self.user.username, self.another_user.username],
            "caption": "test caption",
            "files": [self.file],
        }
        res = self.launch(data)
        self.assertEqual(res.status_code, 201, res.json())

    def test_duplicate_tag(self) -> None:
        data = {
            "tags": [self.user.username, self.user.username],
            "caption": "test caption",
            "files": [self.file],
        }
        res = self.launch(data)
        self.assertEqual(res.status_code, 201, res.json())
        tag_count = m.Post.objects.last().tags.count()
        self.assertEqual(
            tag_count,
            1,
            f"tag count was supposed to be 1, but its {tag_count}",
        )

    def test_duplicate_file(self) -> None:
        data = {
            "tags": [self.user.username],
            "caption": "test caption",
            "files": [self.file, self.file],
        }
        res = self.launch(data)
        self.assertEqual(res.status_code, 201, res.json())
        file_counts = m.Post.objects.last().postfile_set.count()
        self.assertEqual(
            file_counts,
            1,
            f"file count was supposed to be 1, but its {file_counts}",
        )

    def test_invalid_tag(self) -> None:
        data = {
            "tags": [self.user.username, "asghar"],
            "caption": "test caption",
            "files": [self.file, self.file],
        }
        res = self.launch(data)
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(
            res.json()["tags"]["code"], "userNotFound", res.json()
        )

    def test_inactive_tag(self) -> None:
        inactive_user = User._create_test_user("asghar")
        inactive_user.is_active = False
        inactive_user.save()
        data = {
            "tags": [inactive_user.username],
            "caption": "test caption",
            "files": [self.file],
        }
        res = self.launch(data)
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(
            res.json()["tags"]["code"], "userNotFound", res.json()
        )

    def test_invalid_file(self) -> None:
        data = {
            "tags": [self.user.username, "asghar"],
            "caption": "test caption",
            "files": [" test "],
        }
        res = self.launch(data)
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(
            res.json()["files"]["code"], "invalidFile", res.json()
        )

    def test_inactive_file(self) -> None:
        # This will create a PostFile as well, since we are creating
        # a PostFile in our init, this one will get the "2" pk id
        # and it will assigned to the created post.
        m.Post._create_test_post(self.user, True)
        data = {
            "tags": [self.user.username],
            "caption": "test caption",
            "files": [2],
        }
        res = self.launch(data)
        self.assertEqual(res.status_code, 400, res.json())
        self.assertEqual(
            res.json()["files"]["code"], "fileNotFound", res.json()
        )
