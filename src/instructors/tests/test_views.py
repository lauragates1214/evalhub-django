from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from surveys.models import Survey


class InstructorDashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_dashboard_url_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("instructors:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_uses_correct_template(self):
        response = self.client.get(reverse("instructors:dashboard"))
        self.assertTemplateUsed(response, "dashboard.html")

    def test_dashboard_shows_sidebar_navigation(self):
        response = self.client.get(reverse("instructors:dashboard"))
        self.assertContains(response, "instructor-sidebar")
        self.assertContains(response, "My Surveys")
        self.assertContains(response, "Create Survey")


class InstructorSurveysListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_surveys_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("instructors:survey_list"))
        self.assertEqual(response.status_code, 302)

    def test_surveys_list_shows_user_surveys(self):
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get(reverse("instructors:survey_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Survey 1")
        self.assertContains(response, "Survey 2")


class InstructorCreateSurveyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_create_survey_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("instructors:create_survey"))
        self.assertEqual(response.status_code, 302)

    def test_get_returns_create_form(self):
        response = self.client.get(reverse("instructors:create_survey"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="survey_name"')

    def test_post_creates_survey_with_name(self):
        self.client.post(
            reverse("instructors:create_survey"), {"survey_name": "Test Survey"}
        )

        self.assertEqual(Survey.objects.count(), 1)
        new_survey = Survey.objects.first()
        self.assertEqual(new_survey.name, "Test Survey")
        self.assertEqual(new_survey.owner, self.user)


class InstructorSurveyDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)
        self.survey = Survey.objects.create(name="Test Survey", owner=self.user)

    def test_survey_detail_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_survey_detail_shows_survey_name(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Survey")

    def test_survey_detail_404_for_nonexistent_survey(self):
        response = self.client.get(reverse("instructors:survey_detail", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_survey_detail_forbidden_for_other_users_survey(self):
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        other_survey = Survey.objects.create(name="Other Survey", owner=other_user)

        response = self.client.get(
            reverse("instructors:survey_detail", args=[other_survey.id])
        )
        self.assertEqual(response.status_code, 403)


class InstructorSurveyResponsesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)
        self.survey = Survey.objects.create(name="Test Survey", owner=self.user)

    def test_survey_responses_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_survey_responses_shows_survey_name(self):
        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Survey")


class InstructorAnalyticsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_analytics_url_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("instructors:analytics"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_analytics_view_returns_200(self):
        response = self.client.get(reverse("instructors:analytics"))
        self.assertEqual(response.status_code, 200)
