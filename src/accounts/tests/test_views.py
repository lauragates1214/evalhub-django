from django.test import TestCase

from tests.base import AuthenticatedTestCase
from accounts.models import User


class LoginRedirectTest(TestCase):
    def test_unauthenticated_root_redirects_to_login(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_instructor_redirected_to_dashboard_after_login(self):
        # All users who login are instructors
        # Students never login - they access surveys anonymously
        instructor = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )

        # Post login credentials
        response = self.client.post(
            "/accounts/login/",
            {"username": "instructor@example.com", "password": "testpass123"},
        )

        # All logged-in users should go to instructor dashboard
        self.assertRedirects(response, "/instructor/")


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
