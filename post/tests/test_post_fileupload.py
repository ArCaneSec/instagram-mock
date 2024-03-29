from http.cookies import SimpleCookie

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from post.models import PostFile
from user.authenticate import generate_jwt_for_test_user
from user.models import User

ENOUGH_DATA = "".join(map(str, range(1, 1025))).encode()


class TestPostUpload(APITestCase):
    def setUp(self):
        self.url = reverse("post:upload")
        self.token = generate_jwt_for_test_user(User._create_test_user("test"))
        self.client.cookies = SimpleCookie({"token": self.token})
        self.launch = lambda data: (
            self.client.put(
                self.url,
                data=data,
                format="multipart",
            )
        )
        self.check_no_post_was_created = lambda: self.assertEqual(
            bool(PostFile.objects.last()), False
        )

    def test_regular_upload(self):
        data = dict(
            content=SimpleUploadedFile("test.jpg", ENOUGH_DATA, "image/jpg")
        )
        res = self.launch(data)
        self.assertEqual(
            res.status_code,
            201,
            f"upload failed with valid data. {res.json()}",
        )
        self.assertEqual(
            bool(PostFile.objects.last()),
            True,
            f"upload was successfull but data wasn't saved on db, {res.json()}",
        )

    def test_invalid_name_extension(self):
        data = dict(
            content=SimpleUploadedFile(
                "test.php", b"somecontent", "application/php"
            )
        )
        res = self.launch(data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["content"]["code"], "invalidExtension")
        self.check_no_post_was_created()

    def test_inconsistent_extension(self):
        data = dict(
            content=SimpleUploadedFile(
                "test.jpeg", b"somecontent", "image/jpg"
            )
        )
        res = self.launch(data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json()["content"]["code"], "inconsistentExtension"
        )
        self.check_no_post_was_created()

    def test_long_name(self):
        data = dict(
            content=SimpleUploadedFile(
                (lambda: "".join(map(str, range(60))))(),
                b"somecontent",
                "image/png",
            )
        )
        res = self.launch(data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], "invalidName")
        self.check_no_post_was_created()

    def test_null_name(self):
        data = dict(
            content=SimpleUploadedFile(
                ".png",
                b"somecontent",
                "image/png",
            )
        )
        res = self.launch(data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], "invalidName")
        self.check_no_post_was_created()

    def test_empty_file(self):
        data = dict(
            content=SimpleUploadedFile(
                "test.png",
                b" ",
                "image/png",
            )
        )
        res = self.launch(data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["content"]["code"], "invalidSize")
        self.check_no_post_was_created()

    def test_post_with_tags(self):
        data = dict(
            content=SimpleUploadedFile("test.jpg", ENOUGH_DATA, "image/jpg"),
            tags=["test"],
        )
        res = self.launch(data)
        self.assertEqual(
            res.status_code, 201, "upload failed with valid data."
        )
