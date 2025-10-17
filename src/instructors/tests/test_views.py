from django.urls import reverse
from django.utils import html

import csv
from io import StringIO

from accounts.models import User
from surveys.forms import EMPTY_QUESTION_ERROR
from surveys.models import Answer, Question, Submission, Survey
from tests.base import AuthenticatedTestCase


class InstructorDashboardViewTest(AuthenticatedTestCase):
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


class InstructorSurveysListViewTest(AuthenticatedTestCase):
    def test_surveys_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("instructors:surveys_list"))
        self.assertEqual(response.status_code, 302)

    def test_surveys_list_shows_user_surveys(self):
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get(reverse("instructors:surveys_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Survey 1")
        self.assertContains(response, "Survey 2")

    def test_returns_surveys_list_partial_for_htmx(self):
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get(
            reverse("instructors:surveys_list"), HTTP_HX_REQUEST="true"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/surveys_list.html")
        self.assertContains(response, "Survey 1")
        self.assertContains(response, "Survey 2")

    def test_survey_names_are_clickable_links_with_htmx(self):
        Survey.objects.create(name="Survey 1", owner=self.user)
        Survey.objects.create(name="Survey 2", owner=self.user)

        response = self.client.get(
            reverse("instructors:surveys_list"), HTTP_HX_REQUEST="true"
        )

        # Check that survey names have htmx attributes
        self.assertContains(response, 'hx-get="')
        self.assertContains(response, 'hx-target="#main-content"')
        self.assertContains(response, "<a", count=2)  # Two surveys = two links


class InstructorCreateSurveyViewTest(AuthenticatedTestCase):
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
        self.assertTemplateUsed(response, "partials/survey_detail.html")
        self.assertContains(response, "Test Survey")

    def test_post_sets_hx_push_url_header(self):
        response = self.client.post(
            reverse("instructors:create_survey"),
            {"survey_name": "Test Survey"},
            HTTP_HX_REQUEST="true",
        )

        survey = Survey.objects.first()
        self.assertEqual(
            response["HX-Push-Url"],
            reverse("instructors:survey_detail", args=[survey.id]),
        )

    def test_post_without_htmx_redirects_to_survey_detail(self):
        response = self.client.post(
            reverse("instructors:create_survey"), {"survey_name": "Test Survey"}
        )
        new_survey = Survey.objects.first()
        self.assertRedirects(
            response, reverse("instructors:survey_detail", args=[new_survey.id])
        )


class InstructorSurveyDetailAccessControlTest(AuthenticatedTestCase):
    def test_survey_detail_requires_login(self):
        survey = self.create_survey()
        self.client.logout()
        response = self.client.get(
            reverse("instructors:survey_detail", args=[survey.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_survey_detail_404_for_nonexistent_survey(self):
        response = self.client.get(reverse("instructors:survey_detail", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_survey_detail_forbidden_for_other_users_survey(self):
        other_user = self.create_user("other@example.com", "pass")
        other_survey = self.create_survey(owner=other_user, name="Other Survey")

        response = self.client.get(
            reverse("instructors:survey_detail", args=[other_survey.id])
        )
        self.assertEqual(response.status_code, 403)


class InstructorSurveyDetailDisplayTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.survey = self.create_survey()

    def test_survey_detail_shows_survey_name(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Survey")

    def test_survey_detail_displays_survey_name_with_id(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertContains(response, "Test Survey")

    def test_survey_detail_displays_questions(self):
        Question.objects.create(survey=self.survey, text="Question 1")
        Question.objects.create(survey=self.survey, text="Question 2")

        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "Question 1")
        self.assertContains(response, "Question 2")

    def test_survey_detail_shows_qr_code(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "qr-code")
        self.assertContains(
            response, reverse("instructors:generate_qr_code", args=[self.survey.id])
        )

    def test_survey_detail_shows_responses_link(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "View Responses")
        self.assertContains(
            response,
            f'<a href="{reverse("instructors:responses_list", args=[self.survey.id])}"',
        )

    def test_survey_detail_shows_export_link(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "Export to CSV")
        self.assertContains(
            response,
            f'href="{reverse("instructors:export_responses", args=[self.survey.id])}"',
        )

    def test_view_responses_link_has_htmx_attributes(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )

        expected_url = reverse("instructors:responses_list", args=[self.survey.id])
        self.assertContains(response, f'hx-get="{expected_url}"')
        self.assertContains(response, 'hx-target="#main-content"')

    def test_view_responses_link_is_accessible(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        responses_url = reverse("instructors:responses_list", args=[self.survey.id])
        self.assertContains(response, responses_url)

        response = self.client.get(responses_url)
        self.assertEqual(response.status_code, 200)


class InstructorSurveyNameEditingTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.survey = self.create_survey()

    def test_survey_detail_has_edit_button_for_name(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )
        self.assertContains(response, "edit-survey-name-btn")

    def test_survey_detail_display_mode_has_edit_button_no_input(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertContains(response, "edit-survey-name-btn")
        self.assertNotContains(response, 'id="survey-name-input"')

    def test_survey_detail_edit_mode_has_input_field(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
            + "?edit_mode=true",
            HTTP_HX_REQUEST="true",
        )

        self.assertContains(response, 'id="survey-name-input"')
        self.assertContains(response, self.survey.name)

    def test_post_updates_survey_name(self):
        self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"survey_name": "Updated Survey Name"},
        )

        self.survey.refresh_from_db()
        self.assertEqual(self.survey.name, "Updated Survey Name")

    def test_htmx_post_updates_survey_name_returns_partial(self):
        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"survey_name": "New Name"},
            HTTP_HX_REQUEST="true",
        )

        self.assertTemplateUsed(response, "partials/survey_name_display.html")
        self.assertContains(response, "New Name")


class InstructorSurveyQuestionManagementTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.survey = self.create_survey()

    def test_post_adds_question_to_survey(self):
        self.client.post(
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

        self.assertContains(response, html.escape("You can't have an empty question"))

    def test_post_with_duplicate_question_shows_error(self):
        Question.objects.create(survey=self.survey, text="Existing question")

        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": "Existing question"},
        )

        self.assertContains(
            response, "You&#x27;ve already got this question in your survey"
        )

    def test_duplicate_question_validation(self):
        Question.objects.create(survey=self.survey, text="Unique question")

        response = self.client.post(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            {"text": "Unique question"},
        )

        self.assertEqual(Question.objects.count(), 1)
        self.assertContains(
            response, "You&#x27;ve already got this question in your survey"
        )

    def test_questions_display_in_correct_order(self):
        q1 = Question.objects.create(survey=self.survey, text="First question")
        q2 = Question.objects.create(survey=self.survey, text="Second question")
        q3 = Question.objects.create(survey=self.survey, text="Third question")

        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        content = response.content.decode()
        pos1 = content.find("First question")
        pos2 = content.find("Second question")
        pos3 = content.find("Third question")

        self.assertLess(pos1, pos2)
        self.assertLess(pos2, pos3)


class InstructorSurveyDetailRenderingTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.survey = self.create_survey()

    def test_returns_survey_editor_partial_for_htmx(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )

        self.assertTemplateUsed(response, "partials/survey_detail.html")
        self.assertTemplateNotUsed(response, "dashboard.html")

    def test_returns_full_dashboard_for_direct_navigation(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id])
        )

        self.assertTemplateUsed(response, "dashboard.html")

    def test_survey_detail_returns_partial_for_htmx(self):
        response = self.client.get(
            reverse("instructors:survey_detail", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/survey_detail.html")


class InstructorSurveyResponsesViewTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.survey = self.create_survey()

    def test_responses_list_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("instructors:responses_list", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_responses_list_shows_survey_name(self):
        response = self.client.get(
            reverse("instructors:responses_list", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Survey")

    def test_responses_page_returns_partial_for_htmx(self):
        response = self.client.get(
            reverse("instructors:responses_list", args=[self.survey.id]),
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/responses_list.html")
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
            reverse("instructors:responses_list", args=[self.survey.id])
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
            reverse("instructors:responses_list", args=[other_survey.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_responses_404_for_nonexistent_survey(self):
        response = self.client.get(reverse("instructors:responses_list", args=[999]))

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
            reverse("instructors:responses_list", args=[self.survey.id])
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
            reverse("instructors:responses_list", args=[self.survey.id])
        )

        self.assertContains(response, "5")
        self.assertContains(response, "Excellent course with great examples!")

    def test_404_response_contains_not_found(self):
        response = self.client.get(reverse("instructors:responses_list", args=[999]))

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Not Found", status_code=404)

    def test_empty_responses_list_has_no_list_items(self):
        Question.objects.create(survey=self.survey, text="Question with no answers")

        response = self.client.get(
            reverse("instructors:responses_list", args=[self.survey.id])
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
            reverse("instructors:responses_list", args=[self.survey.id])
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


class InstructorExportResponsesViewTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.survey = self.create_survey()

    def test_export_url_exists(self):
        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_export_returns_csv_file(self):
        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )

        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=", response["Content-Disposition"])

    def test_export_includes_question_headers(self):
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
        self.client.logout()
        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_export_forbidden_for_other_users_survey(self):
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        other_survey = Survey.objects.create(name="Other Survey", owner=other_user)

        response = self.client.get(
            reverse("instructors:export_responses", args=[other_survey.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_export_includes_comments(self):
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
            comment_text="Excellent teaching!",
            submission=submission,
        )

        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )

        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        header = next(csv_reader)
        data_row = next(csv_reader)

        # Check that comment is included in export
        # Depending on implementation, might be in same cell or separate column
        row_text = " ".join(data_row)
        self.assertIn("5", row_text)
        self.assertIn("Excellent teaching!", row_text)

    def test_export_with_different_question_types(self):
        # Create different question types
        text_q = Question.objects.create(
            survey=self.survey, text="Your name", question_type="text"
        )
        rating_q = Question.objects.create(
            survey=self.survey,
            text="Rate this",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )
        checkbox_q = Question.objects.create(
            survey=self.survey,
            text="Select topics",
            question_type="checkbox",
            options=["Python", "Django", "Testing"],
        )
        yes_no_q = Question.objects.create(
            survey=self.survey,
            text="Would you recommend?",
            question_type="yes_no",
            options=["Yes", "No"],
        )

        submission = Submission.objects.create(survey=self.survey)
        Answer.objects.create(
            question=text_q, answer_text="John Doe", submission=submission
        )
        Answer.objects.create(
            question=rating_q,
            answer_text="4",
            comment_text="Good course",
            submission=submission,
        )
        Answer.objects.create(
            question=checkbox_q,
            answer_text="Python,Django",  # Assuming comma-separated for multiple selections
            submission=submission,
        )
        Answer.objects.create(
            question=yes_no_q, answer_text="Yes", submission=submission
        )

        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )

        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        header = next(csv_reader)
        data_row = next(csv_reader)

        # Verify all question types are exported correctly
        self.assertIn("Your name", header)
        self.assertIn("Rate this", header)
        self.assertIn("Select topics", header)
        self.assertIn("Would you recommend?", header)

        row_text = " ".join(data_row)
        self.assertIn("John Doe", row_text)
        self.assertIn("4", row_text)
        self.assertIn("Python", row_text)
        self.assertIn("Django", row_text)
        self.assertIn("Yes", row_text)

    def test_export_filename_format(self):
        response = self.client.get(
            reverse("instructors:export_responses", args=[self.survey.id])
        )

        content_disposition = response["Content-Disposition"]

        # Check that filename includes survey ID
        self.assertIn(f"survey_{self.survey.id}", content_disposition.lower())
        self.assertIn("_responses.csv", content_disposition.lower())


class QuestionValidationErrorDisplayTest(AuthenticatedTestCase):
    def test_empty_question_shows_is_invalid_class(self):
        survey = self.create_survey()

        response = self.client.post(
            reverse("instructors:survey_detail", args=[survey.id]),
            {"text": ""},  # Empty question
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "is-invalid")
        # Check for the error message (it will be HTML-escaped in the response)
        self.assertContains(
            response, "empty question"
        )  # Just check for part of the message
