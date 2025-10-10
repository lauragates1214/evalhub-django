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

    def test_post_sets_hx_push_url_header(self):
        response = self.client.post(
            "/dashboard/surveys/new/",
            {"survey_name": "Test Survey"},
            HTTP_HX_REQUEST="true",
        )

        survey = Survey.objects.first()
        self.assertEqual(response["HX-Push-Url"], f"/dashboard/surveys/{survey.id}/")


class DashboardMySurveysViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)

    def test_returns_survey_list_partial_for_htmx(self):
        # Create some surveys
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get("/dashboard/surveys/", HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/survey_list.html")
        self.assertContains(response, "Survey 1")
        self.assertContains(response, "Survey 2")

    def test_survey_names_are_clickable_links(self):
        # Create some surveys
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get("/dashboard/surveys/", HTTP_HX_REQUEST="true")

        # Check that survey names are rendered as links with htmx attributes
        self.assertContains(response, 'hx-get="/dashboard/surveys/')
        self.assertContains(response, 'hx-target="#main-content"')
        self.assertContains(response, "<a", count=2)  # Two surveys = two links


class DashboardSurveyDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)
        self.survey = Survey.objects.create(name="Test Survey", owner=self.user)

    def test_returns_survey_editor_partial_for_htmx(self):
        response = self.client.get(
            f"/dashboard/surveys/{self.survey.id}/", HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/survey_editor.html")
        self.assertContains(response, "Test Survey")

    def test_returns_full_dashboard_for_direct_navigation(self):
        response = self.client.get(f"/dashboard/surveys/{self.survey.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertEqual(response.context["initial_view"], "survey_detail")
        self.assertEqual(response.context["survey"], self.survey)

    def test_404_for_nonexistent_survey(self):
        response = self.client.get("/dashboard/surveys/999/")
        self.assertEqual(response.status_code, 404)

    def test_403_for_other_users_survey(self):
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        other_survey = Survey.objects.create(name="Other Survey", owner=other_user)

        response = self.client.get(f"/dashboard/surveys/{other_survey.id}/")
        self.assertEqual(
            response.status_code, 404
        )  # Should be 404, not expose existence
