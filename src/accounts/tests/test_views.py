from django.test import TestCase


class LoginViewTest(TestCase):
    def test_shows_success_message_after_login(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create(email="test@example.com")
        user.set_password("password")
        user.save()

        response = self.client.post(
            "/accounts/login/",
            {"username": "test@example.com", "password": "password"},
            follow=True,
        )

        self.assertContains(response, "You have been logged in successfully")
