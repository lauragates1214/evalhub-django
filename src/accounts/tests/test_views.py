from django.test import TestCase

from tests.base import AuthenticatedTestCase
from accounts.models import User


class LoginViewTest(TestCase):
    def test_shows_success_message_after_login(self):
        user = User.objects.create(email="test@example.com")
        user.set_password("password")
        user.save()

        response = self.client.post(
            "/accounts/login/",
            {"username": "test@example.com", "password": "password"},
            follow=True,
        )

        self.assertContains(response, "You have been logged in successfully")


class LogoutViewTest(AuthenticatedTestCase):
    # setUp inherited from AuthenticatedTestCase - creates and logs in self.user

    def test_shows_success_message_after_logout(self):
        # Then log out
        response = self.client.post("/accounts/logout/", follow=True)

        self.assertContains(response, "You have been logged out")
