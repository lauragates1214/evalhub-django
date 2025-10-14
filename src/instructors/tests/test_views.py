from django.test import TestCase
from django.urls import reverse
from django.utils import html

from surveys.forms import EMPTY_QUESTION_ERROR
from accounts.models import User
from surveys.models import Question, Survey


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

    def test_returns_survey_list_partial_for_htmx(self):
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get(
            reverse("instructors:survey_list"), HTTP_HX_REQUEST="true"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/survey_list.html")
        self.assertContains(response, "Survey 1")
        self.assertContains(response, "Survey 2")

    def test_survey_names_are_clickable_links_with_htmx(self):
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get(
            reverse("instructors:survey_list"), HTTP_HX_REQUEST="true"
        )

        # Check that survey names have htmx attributes
        self.assertContains(response, 'hx-get="')
        self.assertContains(response, 'hx-target="#main-content"')
        self.assertContains(response, "<a", count=2)  # Two surveys = two links


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

    def test_get_returns_create_form_partial_for_htmx(self):
        response = self.client.get(
            reverse("instructors:create_survey"), HTTP_HX_REQUEST="true"
        )
        self.assertTemplateUsed(response, "partials/create_survey.html")

    def test_get_returns_full_page_without_htmx(self):
        response = self.client.get(reverse("instructors:create_survey"))
        self.assertTemplateUsed(response, "dashboard.html")

    def test_post_returns_survey_editor_partial_for_htmx(self):
        response = self.client.post(
            reverse("instructors:create_survey"),
            {"survey_name": "Test Survey"},
            HTTP_HX_REQUEST="true",
        )
        self.assertTemplateUsed(response, "partials/survey_editor.html")
        self.assertContains(response, "Test Survey")

    def test_post_sets_hx_push_url_header(self):
        response = self.client.post(
            reverse("instructors:create_survey"),
            {"survey_name": "Test Survey"},
            HTTP_HX_REQUEST="true",
        )

        survey = Survey.objects.first()
        self.assertEqual(response["HX-Push-Url"], f"/instructor/surveys/{survey.id}/")

    def test_post_without_htmx_redirects_to_survey_detail(self):
        response = self.client.post(
            reverse("instructors:create_survey"), {"survey_name": "Test Survey"}
        )
        new_survey = Survey.objects.first()
        self.assertRedirects(
            response, reverse("instructors:survey_detail", args=[new_survey.id])
        )


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

    def test_post_adds_question_to_survey(self):
        """Test POST request adds a question to the survey"""
        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": "How was the session?"},
        )

        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.first()
        self.assertEqual(new_question.text, "How was the session?")
        self.assertEqual(new_question.survey, self.survey)

    def test_post_with_invalid_question_shows_error(self):
        """Test POST with empty question text shows validation error"""
        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": ""},
        )

        self.assertEqual(Question.objects.count(), 0)
        self.assertContains(response, html.escape(EMPTY_QUESTION_ERROR))

    def test_survey_detail_displays_questions(self):
        """Test that survey detail page shows all questions for that survey"""
        from surveys.models import Question

        Question.objects.create(survey=self.survey, text="Question 1")
        Question.objects.create(survey=self.survey, text="Question 2")

        # Create another survey with a question to ensure we're filtering correctly
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        other_survey = Survey.objects.create(name="Other Survey", owner=other_user)
        Question.objects.create(survey=other_survey, text="Other question")

        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "Question 1")
        self.assertContains(response, "Question 2")
        self.assertNotContains(response, "Other question")

    def test_duplicate_question_validation(self):
        """Test that duplicate questions show validation error"""
        from django.utils import html
        from surveys.models import Question
        from surveys.forms import DUPLICATE_QUESTION_ERROR

        Question.objects.create(survey=self.survey, text="Unique question")

        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": "Unique question"},  # Duplicate
        )

        self.assertEqual(Question.objects.count(), 1)  # No new question created
        self.assertContains(response, html.escape(DUPLICATE_QUESTION_ERROR))

    def test_survey_detail_shows_qr_code(self):
        """Test that survey detail page displays QR code"""
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "qr-code")
        self.assertContains(response, f"/surveys/{self.survey.id}/qr/")

    def test_survey_detail_shows_responses_link(self):
        """Test that survey detail page shows link to view responses"""
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "View Responses")
        self.assertContains(
            response, reverse("instructors:survey_responses", args=[self.survey.id])
        )

    def test_survey_detail_shows_export_link(self):
        """Test that survey detail page shows export to CSV link"""
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "Export to CSV")
        self.assertContains(response, f"/surveys/{self.survey.id}/export/")

    def test_returns_survey_editor_partial_for_htmx(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/survey_editor.html")
        self.assertContains(response, "Test Survey")

    def test_returns_full_dashboard_for_direct_navigation(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertEqual(response.context["initial_view"], "survey_detail")
        self.assertEqual(response.context["survey"], self.survey)

    def test_view_responses_link_has_htmx_attributes(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )

        # Check that View Responses link has htmx attributes
        self.assertContains(response, "hx-get=")
        self.assertContains(response, 'hx-target="#main-content"')
        # The link should point to the instructor URL
        self.assertContains(response, "/instructor/surveys/")
        self.assertContains(response, "/responses/")


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

    def test_responses_page_returns_partial_for_htmx(self):
        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/survey_responses.html")
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


class InstructorExportResponsesViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.client.force_login(self.user)
        self.survey = Survey.objects.create(name="Test Survey", owner=self.user)

    def test_export_url_exists(self):
        """Test that export endpoint returns 200"""
        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_export_returns_csv_file(self):
        """Test that response has correct CSV headers"""
        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )

        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=", response["Content-Disposition"])

    def test_export_includes_question_headers(self):
        """Test that CSV includes question headers"""
        from surveys.models import Question
        import csv
        from io import StringIO

        Question.objects.create(
            survey=self.survey, text="Question 1", question_type="text"
        )
        Question.objects.create(
            survey=self.survey,
            text="Question 2",
            question_type="rating",
            options=[1, 2, 3],
        )

        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        header = next(csv_reader)

        self.assertIn("Question 1", header)
        self.assertIn("Question 2", header)

    def test_export_includes_answer_data(self):
        """Test that CSV includes answer data"""
        from surveys.models import Question, Submission, Answer
        import csv
        from io import StringIO

        q1 = Question.objects.create(
            survey=self.survey, text="Question 1", question_type="text"
        )
        q2 = Question.objects.create(
            survey=self.survey, text="Question 2", question_type="text"
        )

        # Create a submission with answers
        submission = Submission.objects.create(survey=self.survey)
        Answer.objects.create(
            question=q1, answer_text="Answer 1A", submission=submission
        )
        Answer.objects.create(
            question=q2, answer_text="Answer 2A", submission=submission
        )

        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)

        self.assertEqual(len(rows), 2)  # Header + 1 data row
        self.assertEqual(rows[0], ["Submission ID", "Question 1", "Question 2"])
        self.assertEqual(rows[1], [str(submission.id), "Answer 1A", "Answer 2A"])

    def test_export_with_no_submissions_only_shows_header(self):
        """Test that CSV with no submissions only has header"""
        from surveys.models import Question
        import csv
        from io import StringIO

        Question.objects.create(
            survey=self.survey, text="Question 1", question_type="text"
        )

        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)

        self.assertEqual(len(rows), 1)  # Only header row
        self.assertEqual(rows[0], ["Submission ID", "Question 1"])

    def test_export_requires_login(self):
        """Test that export requires authentication"""
        self.client.logout()
        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_export_forbidden_for_other_users_survey(self):
        """Test that instructors can't export other instructors' surveys"""
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        other_survey = Survey.objects.create(name="Other Survey", owner=other_user)

        response = self.client.get(
            reverse("instructors:export_responses", args=[other_survey.id])
        )
        self.assertEqual(response.status_code, 403)
