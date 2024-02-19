from http.cookies import SimpleCookie

from django.http import HttpResponse
from django.urls import reverse
from rest_framework.test import APITestCase

from user.authenticate import generate_jwt_for_test_user
from user.models import User


class ViewTests(APITestCase):

    def create_user(self, username: str, is_private: bool = False) -> User:
        return User._create_test_user(username, is_private)

    def create_url(self, path: str, args: list[any]) -> None:
        if args:
            self.url = reverse(path, args=args)
            return

        self.url = reverse(path)

    def set_cookie(self, cookie_name: str, user: User) -> None:
        self.client.cookies = SimpleCookie(
            {cookie_name: generate_jwt_for_test_user(user)}
        )

    def launch_post(
        self, data: dict = None, content_type: str = "json"
    ) -> HttpResponse:
        return self.client.post(self.url, data, content_type)
    
    def launch_delete(
    self, data: dict = None, content_type: str = "json"
) -> HttpResponse:
        return self.client.delete(self.url, data, content_type)