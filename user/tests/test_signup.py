from django.urls import reverse
from rest_framework.test import APITestCase

from .. import models as m

# Create your tests here.


class SingUpTest(APITestCase):

    def setUp(self):
        self.url = reverse("user:sign_up")
        self.data = {
            "username": "arcane",
            "firstName": "arcane firstname",
            "lastName": "arcane lastname",
            "nickName": "ArCane",
            "phoneNumber": "01234567891",
            "email": "arcane@test.com",
            "password": "MmNn123mm",
        }
        m.User.objects.create(
            username="test",
            nickname="test",
            first_name="test",
            last_name="test",
            email="test@test.com",
            phone_number="01234567892",
            password="123",
        )

    def test_regular_signup(self):
        res = self.client.post(
            self.url,
            self.data,
            format="json",
        )
        self.assertEqual(res.status_code, 201)

    def test_invalid_phone_signup(self):
        self.data["phoneNumber"] = "sss"
        res = self.client.post(
            self.url,
            self.data,
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_weak_password_signup(self):
        self.data["password"] = "mmnn"
        res = self.client.post(
            self.url,
            self.data,
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_non_unique_username(self):
        self.data["username"] = "test"
        res = self.client.post(
            self.url,
            self.data,
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["username"]["code"], "nonUniqueUserName")

    def test_non_unique_email(self):
        self.data["email"] = "test@test.com"
        res = self.client.post(
            self.url,
            self.data,
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["email"]["code"], "nonUniqueEmail")

    def test_non_unique_phone(self):
        self.data["phoneNumber"] = "01234567892"
        res = self.client.post(
            self.url,
            self.data,
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json()["phoneNumber"]["code"], "nonUniquePhoneNumber"
        )

