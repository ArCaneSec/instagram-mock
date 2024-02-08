from datetime import datetime

import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from .. import models as m


class Login(APITestCase):
    def setUp(self):
        self.url = reverse("user:login")
        m.User.objects.create(
            username="test",
            nickname="test",
            first_name="test",
            last_name="test",
            email="test@test.com",
            phone_number="01234567892",
            password="123",
        )
        self.data = {"username": "test", "password": "123"}

    def test_regular_login(self):
        res = self.client.post(self.url, self.data, "json")
        self.assertEqual(res.status_code, 200, "login failed with valid data.")

    def test_jwt_token(self):
        res = self.client.post(self.url, self.data, "json")
        token = jwt.decode(
            res.cookies["token"].value,
            key=settings.SECRET_KEY,
            algorithms="HS256",
        )
        self.assertEqual(
            token["username"], self.data["username"], "Jwt token in incorrect."
        )
        exp_datetime = datetime.fromtimestamp(token["exp"])
        self.assertGreater(
            exp_datetime, datetime.now(), "Invalid expire date."
        )

    def test_invalid_username(self):
        self.data["username"] = "invalid"
        res = self.client.post(self.url, self.data, "json")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["code"], "invalidCredentials")

    def test_invalid_password(self):
        self.data["password"] = "invalid"
        res = self.client.post(self.url, self.data, "json")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["code"], "invalidCredentials")