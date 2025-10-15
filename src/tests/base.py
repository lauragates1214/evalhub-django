from django.test import TestCase
import lxml.html

from accounts.models import User
from surveys.models import Survey


class AuthenticatedTestCase(TestCase):
    """Base test class with authenticated user and helper methods"""

    def setUp(self):
        """Create and log in a test user"""
        self.user = self.create_user("test@example.com")
        self.client.login(username=self.user.email, password="password")

    def create_user(self, email, password="password"):
        """Helper method to create a user with password"""
        user = User.objects.create(email=email)
        user.set_password(password)
        user.save()
        return user

    def create_survey(self, owner=None, name="Test Survey"):
        """Helper to create a survey with optional owner"""
        if owner is None:
            owner = self.user
        return Survey.objects.create(owner=owner, name=name)

    def parse_html(self, response):
        """Parse HTML response into lxml object"""
        return lxml.html.fromstring(response.content)

    def get_form_by_action(self, response, action_url):
        """Get form element matching the action URL"""
        parsed = self.parse_html(response)
        forms = parsed.cssselect("form[method=POST]")
        matching_forms = [form for form in forms if form.get("action") == action_url]
        return matching_forms[0] if matching_forms else None
