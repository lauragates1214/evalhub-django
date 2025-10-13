from django.test import TestCase
from django.urls import reverse


class InstructorURLTests(TestCase):
    """Test that instructor URLs resolve correctly"""

    def test_instructor_home_url_resolves(self):
        """Test /instructor/ resolves to instructor dashboard view"""
        url = reverse("instructors:dashboard")
        self.assertEqual(url, "/instructor/")

    def test_instructor_surveys_list_url_resolves(self):
        """Test /instructor/surveys/ resolves to surveys list view"""
        url = reverse("instructors:survey_list")
        self.assertEqual(url, "/instructor/surveys/")

    def test_instructor_create_survey_url_resolves(self):
        """Test /instructor/surveys/create/ resolves to create survey view"""
        url = reverse("instructors:create_survey")
        self.assertEqual(url, "/instructor/surveys/create/")

    def test_instructor_survey_detail_url_resolves(self):
        """Test /instructor/surveys/<id>/ resolves to survey detail view"""
        url = reverse("instructors:survey_detail", args=[1])
        self.assertEqual(url, "/instructor/surveys/1/")

    def test_instructor_survey_responses_url_resolves(self):
        """Test /instructor/surveys/<id>/responses/ resolves to responses view"""
        url = reverse("instructors:survey_responses", args=[1])
        self.assertEqual(url, "/instructor/surveys/1/responses/")
