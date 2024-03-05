from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from utils.configs import _JWT_CONFIG

from .. import models as m


class Login(APITestCase):
    def setUp(self):
        self.url = reverse("user:login")
        m.User._create_test_user("test")
        self.data = {"username": "test", "password": "test"}

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
            exp_datetime,
            datetime.now()
            + timedelta(days=_JWT_CONFIG.expire_day_duration),
            "Invalid expire date.",
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

    def test_inactive_user(self):
        user = m.User._create_test_user("another_test")
        user.is_active = False
        user.save()
        res = self.client.post(
            self.url,
            {"username": "another_test", "password": "another_test"},
            "json",
        )
        self.assertEqual(res.status_code, 404, res.json())
