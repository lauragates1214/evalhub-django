from django.test import TestCase
from django.urls import reverse


class StudentURLTests(TestCase):
    """Test that student URLs resolve correctly"""

    def test_student_survey_url_resolves(self):
        """Test /student/survey/<id>/ resolves to survey taking view"""
        url = reverse("students:survey", args=[1])
        self.assertEqual(url, "/student/survey/1/")
