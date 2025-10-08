from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from surveys.models import Survey


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_dashboard_url_requires_login(self):
        self.client.logout()
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_uses_correct_template(self):
        response = self.client.get("/dashboard/")
        self.assertTemplateUsed(response, "dashboard.html")

    def test_dashboard_shows_sidebar_navigation(self):
        response = self.client.get("/dashboard/")
        self.assertContains(response, "dashboard-sidebar")
        self.assertContains(response, "My Surveys")
        self.assertContains(response, "Create Survey")


class DashboardCreateSurveyViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_get_returns_create_form_partial_for_htmx(self):
        response = self.client.get("/dashboard/surveys/new/", HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "partials/create_survey.html")

    def test_get_returns_full_page_without_htmx(self):
        response = self.client.get("/dashboard/surveys/new/")
        self.assertTemplateUsed(response, "dashboard.html")

    def test_post_creates_survey_with_name(self):
        response = self.client.post(
            "/dashboard/surveys/new/",
            {"survey_name": "Test Survey"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(Survey.objects.count(), 1)
        new_survey = Survey.objects.first()
        self.assertEqual(new_survey.name, "Test Survey")
        self.assertEqual(new_survey.owner, self.user)

    def test_post_returns_survey_editor_partial_for_htmx(self):
        response = self.client.post(
            "/dashboard/surveys/new/",
            {"survey_name": "Test Survey"},
            HTTP_HX_REQUEST="true",
        )
        self.assertTemplateUsed(response, "partials/survey_editor.html")
        self.assertContains(response, "Test Survey")

    def test_post_without_htmx_redirects_to_survey_page(self):
        response = self.client.post(
            "/dashboard/surveys/new/", {"survey_name": "Test Survey"}
        )
        new_survey = Survey.objects.first()
        self.assertRedirects(response, f"/surveys/{new_survey.id}/")
