from http.cookies import SimpleCookie

from django.urls import reverse
from rest_framework.test import APITestCase

from ..authenticate import generate_jwt_token
from ..models import User
from ..utils import generate_expire_date


class AuthTest(APITestCase):
    def setUp(self):
        user = User._create_test_user("test")
        self.data = {
            "username": "test",
            "nickname": "test nickname",
            "first_name": "test first_name",
            "last_name": "test last_name",
            "profile": None,
            "biography": None,
            "email": "test@test.com",
            "phone_number": "test",
            "total_followers": 0,
            "total_followings": 0,
        }
        self.token = generate_jwt_token(user, generate_expire_date())
        self.url = reverse("user:dashboard")

    def test_with_valid_token(self):
        self.client.cookies = SimpleCookie({"token": self.token})
        res = self.client.get(self.url)
        self.assertEqual(
            res.status_code, 200, "Invalid response code with valid token."
        )
        self.assertEqual(
            res.json(), self.data, "Invalid personnal data with valid token."
        )

    def test_empty_token(self):
        self.client.cookies = SimpleCookie()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)

    def test_invalid_header(self):
        cookie = SimpleCookie(
            {
                "token": "eyJleHAiOjE3MDg2MTc4MzksInVzZXJuYW1lIjoiYXJjYW5lIn0"
                ".NgdMl11RNSNI6wC3KZU3UKEooWNPUfQKbPZMsdrAmCI"
            }
        )
        self.client.cookies = cookie
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()["code"], "forbidden")

    def test_invalid_payload(self):
        cookie = SimpleCookie(
            {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNzA4NjM1NDA3fQ."
                "cDAqq85XBdnQd6q44b_pRhqGr5NbPBSOcOT8RdPfjJc"
            }
        )
        self.client.cookies = cookie
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.json()["code"], "forbidden")

    def test_expired_token(self):
        cookie = SimpleCookie(
            {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJ1c2VybmFtZSI6ImFyY2FuZSIsImV4cCI6MTcwNDcyMjM5NX0."
                "0MyvIYSowt5o_Jw4YNw9P2TaSKgqeq6Fy1GnCh2WZ5U"
            }
        )
        self.client.cookies = cookie
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
