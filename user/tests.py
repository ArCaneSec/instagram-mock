from django.urls import reverse
from rest_framework.test import APITestCase

from . import models as m

# Create your tests here.


class AuthTest(APITestCase):
    def test_regular_signup(self):
        url = reverse("user:sign_up")
        data = {
            "username": "test",
            "firstName": "test firstname",
            "lastName": "test lastname",
            "nickName": "TesT",
            "phoneNumber": "01234567891",
            "password": "MmNn123mm",
        }
        res = self.client.post(
            url,
            data,
            format="json",
        )
        self.assertEqual(res.status_code, 201)

    def test_invalid_phone_signup(self):
        url = reverse("user:sign_up")
        data = {
            "username": "test",
            "firstName": "test firstname",
            "lastName": "test lastname",
            "nickName": "TesT",
            "phoneNumber": "sss",
            "password": "MmNn123mm",
        }
        res = self.client.post(
            url,
            data,
            format="json",
        )
        self.assertNotEqual(res.status_code, 201)

    def test_weak_password_signup(self):
        url = reverse("user:sign_up")
        data = {
            "username": "test",
            "firstName": "test firstname",
            "lastName": "test lastname",
            "nickName": "TesT",
            "phoneNumber": "01234567891",
            "password": "mmnn",
        }
        res = self.client.post(
            url,
            data,
            format="json",
        )
        self.assertNotEqual(res.status_code, 201)

    def test_non_unique_username(self):
        m.User.objects.create(
            username="test",
            nickname="test",
            first_name="test",
            last_name="test",
            phone_number="test",
            password="123",
        )
        url = reverse("user:sign_up")
        data = {
            "username": "test",
            "firstName": "test firstname",
            "lastName": "test lastname",
            "nickName": "TesT",
            "phoneNumber": "01234567891",
            "password": "mmnn",
        }
        res = self.client.post(
            url,
            data,
            format="json",
        )
        self.assertNotEqual(res.status_code, 201)
        self.assertEqual(res.json()["username"]["code"], "nonUniqueUserName")
