from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from accounts.models import User
from surveys.models import Survey


class NoAnalyticsFeatureTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)
        self.survey = Survey.objects.create(name="Test Survey", owner=self.user)

    def test_analytics_url_returns_404(self):
        """Analytics URL should not exist"""
        response = self.client.get("/instructor/analytics/")
        self.assertEqual(response.status_code, 404)

    def test_analytics_url_name_does_not_exist(self):
        """Analytics URL name should not be reversible"""
        with self.assertRaises(NoReverseMatch):
            reverse("instructors:analytics")

    def test_dashboard_template_has_no_analytics_link(self):
        """Dashboard sidebar should not include analytics"""
        response = self.client.get(reverse("instructors:dashboard"))
        self.assertNotContains(response, "Analytics")
        self.assertNotContains(response, "/instructor/analytics/")
        self.assertNotContains(response, 'hx-get="/instructor/analytics/"')

    def test_survey_detail_has_no_analytics_link(self):
        """Survey detail page should not mention analytics"""
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        # Should have View Responses but not Analytics
        self.assertContains(response, "View Responses")
        self.assertNotContains(response, "Analytics")
        self.assertNotContains(response, "Analyze")
        self.assertNotContains(response, "Statistics")

    def test_survey_responses_page_has_no_analytics_features(self):
        """Response page should show raw data without analytics"""
        from surveys.models import Question, Submission, Answer

        question = Question.objects.create(survey=self.survey, text="Test Question")
        submission = Submission.objects.create(survey=self.survey)
        Answer.objects.create(
            question=question, answer_text="Test Answer", submission=submission
        )

        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )

        # Should show raw responses
        self.assertContains(response, "Test Question")
        self.assertContains(response, "Test Answer")

        # Should not show analytics features
        self.assertNotContains(response, "Average")
        self.assertNotContains(response, "Chart")
        self.assertNotContains(response, "Graph")
        self.assertNotContains(response, "Statistics")
        self.assertNotContains(response, "Analysis")
