from django.test import TestCase
from django.urls import reverse
from django.utils import html

from unittest import skip

from surveys.forms import EMPTY_QUESTION_ERROR
from accounts.models import User
from surveys.models import Answer, Question, Submission, Survey


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
        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": "How was the session?"},
        )

        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.first()
        self.assertEqual(new_question.text, "How was the session?")
        self.assertEqual(new_question.survey, self.survey)

    def test_post_with_invalid_question_shows_error(self):
        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": ""},
        )

        self.assertEqual(Question.objects.count(), 0)
        self.assertContains(response, html.escape(EMPTY_QUESTION_ERROR))

    def test_survey_detail_displays_questions(self):
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
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "qr-code")
        self.assertContains(response, f"/surveys/{self.survey.id}/qr/")

    def test_survey_detail_shows_responses_link(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "View Responses")
        self.assertContains(
            response, reverse("instructors:survey_responses", args=[self.survey.id])
        )

    def test_survey_detail_shows_export_link(self):
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

    def test_post_with_duplicate_question_shows_error(self):
        from surveys.forms import DUPLICATE_QUESTION_ERROR

        Question.objects.create(survey=self.survey, text="Existing question")

        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": "Existing question"},
        )

        self.assertEqual(Question.objects.count(), 1)  # No new question created
        self.assertContains(response, html.escape(DUPLICATE_QUESTION_ERROR))

    def test_survey_detail_returns_partial_for_htmx(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/survey_editor.html")
        self.assertContains(response, "Test Survey")

    def test_questions_display_in_correct_order(self):
        q1 = Question.objects.create(survey=self.survey, text="First question")
        q2 = Question.objects.create(survey=self.survey, text="Second question")
        q3 = Question.objects.create(survey=self.survey, text="Third question")

        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        # Check that questions appear in the correct order in the HTML
        content = response.content.decode()
        pos_q1 = content.find("First question")
        pos_q2 = content.find("Second question")
        pos_q3 = content.find("Third question")

        self.assertLess(pos_q1, pos_q2)
        self.assertLess(pos_q2, pos_q3)

    def test_post_updates_survey_name(self):
        # Only include this if you've implemented survey name editing
        # Check if your view handles a 'survey_name' field
        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"survey_name": "Updated Survey Name"},
        )

        self.survey.refresh_from_db()
        self.assertEqual(self.survey.name, "Updated Survey Name")

    def test_htmx_post_updates_survey_name_returns_partial(self):
        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"survey_name": "HTMX Updated Name"},
            HTTP_HX_REQUEST="true",
        )

    def test_survey_detail_displays_survey_name_with_id(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)
        # Check that the survey name is wrapped in an element with the right ID
        self.assertContains(response, 'id="survey-name-display"')
        self.assertContains(response, "Test Survey")  # The survey name from setUp

    def test_survey_detail_has_edit_button_for_name(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertContains(response, 'id="edit-survey-name-btn"')

    def test_survey_detail_display_mode_has_edit_button_no_input(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        # Should have the edit button
        self.assertContains(response, 'id="edit-survey-name-btn"')
        # Should NOT have the input field yet
        self.assertNotContains(response, 'id="survey-name-input"')
        # Should show the survey name in display mode
        self.assertContains(response, 'id="survey-name-display"')

    def test_survey_detail_edit_mode_has_input_field(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
            + "?edit_mode=true",
            HTTP_HX_REQUEST="true",
        )
        # Should have the input field in edit mode
        self.assertContains(response, 'id="survey-name-input"')
        self.assertContains(response, 'name="survey_name"')
        # Should have the current survey name as the value
        self.assertContains(response, 'value="Test Survey"')

    def test_forbidden_response_contains_403_in_body(self):
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        other_survey = Survey.objects.create(name="Other Survey", owner=other_user)

        response = self.client.get(
            reverse("instructors:survey_detail", args=[other_survey.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "403", status_code=403)

    def test_view_responses_link_is_accessible(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        # Check the link exists
        self.assertContains(
            response,
            f'href="{reverse("instructors:survey_responses", args=[self.survey.id])}"',
        )
        # Check it contains the text "View Responses"
        self.assertContains(response, "View Responses")
        # Check it's an anchor tag by looking for the opening tag with href
        self.assertContains(
            response,
            f'<a href="{reverse("instructors:survey_responses", args=[self.survey.id])}"',
        )


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

    def test_responses_page_displays_actual_submissions(self):
        q1 = Question.objects.create(survey=self.survey, text="Question 1")
        q2 = Question.objects.create(survey=self.survey, text="Question 2")

        submission1 = Submission.objects.create(survey=self.survey)
        Answer.objects.create(
            question=q1, answer_text="Answer 1A", submission=submission1
        )
        Answer.objects.create(
            question=q2, answer_text="Answer 2A", submission=submission1
        )

        submission2 = Submission.objects.create(survey=self.survey)
        Answer.objects.create(
            question=q1, answer_text="Answer 1B", submission=submission2
        )

        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )

        self.assertContains(response, "Answer 1A")
        self.assertContains(response, "Answer 2A")
        self.assertContains(response, "Answer 1B")

    def test_responses_forbidden_for_other_users_survey(self):
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        other_survey = Survey.objects.create(name="Other Survey", owner=other_user)

        response = self.client.get(
            reverse("instructors:survey_responses", args=[other_survey.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_responses_404_for_nonexistent_survey(self):
        response = self.client.get(reverse("instructors:survey_responses", args=[999]))

        self.assertEqual(response.status_code, 404)

    def test_responses_grouped_by_question(self):
        q1 = Question.objects.create(survey=self.survey, text="Question 1")
        q2 = Question.objects.create(survey=self.survey, text="Question 2")

        submission = Submission.objects.create(survey=self.survey)
        Answer.objects.create(
            question=q1, answer_text="Answer to Q1", submission=submission
        )
        Answer.objects.create(
            question=q2, answer_text="Answer to Q2", submission=submission
        )

        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )

        content = response.content.decode()

        # Check that questions appear as headers/groups
        self.assertContains(response, "Question 1")
        self.assertContains(response, "Question 2")

        # Check that Q1 appears before its answer
        pos_q1 = content.find("Question 1")
        pos_a1 = content.find("Answer to Q1")
        self.assertLess(pos_q1, pos_a1)

        # Check that Q2 appears before its answer
        pos_q2 = content.find("Question 2")
        pos_a2 = content.find("Answer to Q2")
        self.assertLess(pos_q2, pos_a2)

    def test_responses_display_comments_with_answers(self):
        question = Question.objects.create(
            survey=self.survey,
            text="Rate this course",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )

        submission = Submission.objects.create(survey=self.survey)
        Answer.objects.create(
            question=question,
            answer_text="5",
            comment_text="Excellent course with great examples!",
            submission=submission,
        )

        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )

        self.assertContains(response, "5")
        self.assertContains(response, "Excellent course with great examples!")

    def test_404_response_contains_not_found(self):
        response = self.client.get(reverse("instructors:survey_responses", args=[999]))

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Not Found", status_code=404)

    def test_empty_survey_responses_has_no_list_items(self):
        Question.objects.create(survey=self.survey, text="Question with no answers")

        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )

        # Check that the response doesn't contain any <li> tags within the response section
        # Since there are no answers, there should be no list items
        content = response.content.decode()

        # Find the section after the question text
        question_pos = content.find("Question with no answers")
        self.assertNotEqual(question_pos, -1, "Question should be in response")

        # Get content after the question
        content_after_question = content[question_pos:]

        # Find the next </ul> tag
        ul_close = content_after_question.find("</ul>")
        if ul_close != -1:
            # Check the content between question and </ul> has no <li> tags
            ul_content = content_after_question[:ul_close]
            self.assertNotIn(
                "<li>", ul_content, "Should have no list items when no answers exist"
            )

    def test_empty_list_html_structure(self):
        Question.objects.create(survey=self.survey, text="Question with no answers")

        response = self.client.get(
            reverse("instructors:survey_responses", args=[self.survey.id])
        )

        # Check that the main content area has no response list items
        # Look specifically in the main-content section
        content = response.content.decode()

        # Find the main-content div
        main_start = content.find('<main id="main-content"')
        main_end = content.find("</main>")
        main_content = content[main_start:main_end]

        # Find the ul after the question
        question_pos = main_content.find("Question with no answers")
        content_after_question = main_content[question_pos:]

        # Check that there are no <li> tags in the response list
        ul_start = content_after_question.find("<ul>")
        ul_end = content_after_question.find("</ul>")
        ul_content = content_after_question[ul_start:ul_end]

        self.assertNotIn("<li>", ul_content, "Response list should be empty")


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
