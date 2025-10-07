from django.test import TestCase
from django.utils import html

import csv
from io import StringIO

from tests.base import AuthenticatedTestCase
from surveys.forms import (
    DUPLICATE_QUESTION_ERROR,
    EMPTY_QUESTION_ERROR,
)
from accounts.models import User
from surveys.models import Answer, Question, Submission, Survey


class NewSurveyAuthTest(TestCase):
    def test_redirects_to_login_if_not_authenticated(self):
        response = self.client.post("/surveys/new", data={"text": "A new question"})
        self.assertRedirects(response, "/accounts/login/?next=/surveys/new")


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_renders_input_form(self):
        response = self.client.get("/")
        parsed = self.parse_html(
            response
        )  # parse HTML into structured object to represent DOM
        [form] = parsed.cssselect(
            "form[method=POST]"
        )  # find form element with method=POST, expect exactly one (hence the brackets)

        self.assertEqual(form.get("action"), "/surveys/new")

        inputs = form.cssselect("input")
        self.assertIn(
            "text", [input.get("name") for input in inputs]
        )  # check at least one input has name=text

    # Add parse_html helper as a module-level function for non-authenticated tests
    @staticmethod
    def parse_html(response):
        import lxml.html

        return lxml.html.fromstring(response.content)

    def test_home_page_displays_survey_name_input(self):
        response = self.client.get("/")

        self.assertContains(response, 'name="survey_name"')
        self.assertContains(response, "Enter a name for your survey")


class NewSurveyTest(AuthenticatedTestCase):
    # setUp inherited from AuthenticatedTestCase

    def test_can_save_a_POST_request(self):
        self.client.post("/surveys/new", data={"text": "A new survey question"})
        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, "A new survey question")

    def test_redirects_after_POST(self):
        response = self.client.post(
            "/surveys/new", data={"text": "A new survey question"}
        )
        new_survey = Survey.objects.get()
        self.assertRedirects(response, f"/surveys/{new_survey.id}/")

    def post_invalid_input(self):
        return self.client.post("/surveys/new", data={"text": ""})

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Question.objects.count(), 0)

    def test_for_invalid_input_renders_survey_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, html.escape(EMPTY_QUESTION_ERROR))

    def test_survey_owner_is_saved_if_user_is_authenticated(self):
        user = self.create_user("a@b.com")
        self.client.force_login(user)
        self.client.post("/surveys/new", data={"text": "new question"})
        new_survey = Survey.objects.get()
        self.assertEqual(new_survey.owner, user)

    def test_can_save_survey_with_name_and_first_question(self):
        self.client.post(
            "/surveys/new",
            data={
                "survey_name": "Q4 Course Evaluation",
                "text": "How did you find the course?",
            },
        )

        self.assertEqual(Survey.objects.count(), 1)
        new_survey = Survey.objects.get()
        self.assertEqual(new_survey.name, "Q4 Course Evaluation")

        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, "How did you find the course?")

    def test_survey_name_defaults_to_Survey_if_not_provided(self):
        self.client.post(
            "/surveys/new",
            data={"survey_name": "", "text": "First question"},  # Empty name
        )

        new_survey = Survey.objects.get()
        self.assertEqual(new_survey.name, "Survey")


class InstructorSurveyViewTest(AuthenticatedTestCase):
    # setUp inherited from AuthenticatedTestCase

    def test_uses_question_template(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/")
        self.assertTemplateUsed(response, "survey.html")

    def test_renders_input_form(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/")
        parsed = self.parse_html(
            response
        )  # parse HTML into structured object to represent DOM
        [form] = parsed.cssselect(
            "form[action^='/surveys/']"
        )  # find survey form element with method=POST, expect exactly one (hence the brackets)

        self.assertEqual(form.get("action"), f"/surveys/{survey.id}/")

        inputs = form.cssselect("input")
        self.assertIn(
            "text", [input.get("name") for input in inputs]
        )  # check at least one input has name=text

    def test_displays_only_questions_for_that_survey(self):
        correct_survey = self.create_survey()
        Question.objects.create(text="Question 1", survey=correct_survey)
        Question.objects.create(text="Question 2", survey=correct_survey)
        other_survey = self.create_survey()
        Question.objects.create(text="Other survey question", survey=other_survey)

        response = self.client.get(f"/surveys/{correct_survey.id}/")

        self.assertContains(response, "Question 1")
        self.assertContains(response, "Question 2")
        self.assertNotContains(response, "Other survey question")

    def test_can_save_a_POST_request_to_an_existing_survey(self):
        other_survey = self.create_survey()
        correct_survey = self.create_survey()

        self.client.post(
            f"/surveys/{correct_survey.id}/",
            data={"text": "A new question for an existing survey"},
        )

        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, "A new question for an existing survey")
        self.assertEqual(new_question.survey, correct_survey)

    def test_POST_redirects_to_survey_view(self):
        other_survey = self.create_survey()
        correct_survey = self.create_survey()

        response = self.client.post(
            f"/surveys/{correct_survey.id}/",
            data={"text": "A new question for an existing survey"},
        )

        self.assertRedirects(response, f"/surveys/{correct_survey.id}/")

    def post_invalid_input(self):
        survey = self.create_survey()
        return self.client.post(f"/surveys/{survey.id}/", data={"text": ""})

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Question.objects.count(), 0)

    def test_for_invalid_input_renders_survey_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "survey.html")

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, html.escape(EMPTY_QUESTION_ERROR))

    def test_for_invalid_input_sets_is_invalid_class(self):
        response = self.post_invalid_input()
        parsed = self.parse_html(response)
        [input] = parsed.cssselect("input[name=text]")
        self.assertIn("is-invalid", set(input.classes))

    def test_duplicate_question_validation_errors_show_on_question_list(self):
        survey = self.create_survey()
        Question.objects.create(survey=survey, text="no twins!")
        response = self.client.post(
            f"/surveys/{survey.id}/",
            data={"text": "no twins!"},
        )

        self.assertTemplateUsed(response, "survey.html")
        self.assertContains(response, html.escape(DUPLICATE_QUESTION_ERROR))

    def test_survey_page_displays_qr_code(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/")
        self.assertContains(response, "qr-code")

    def test_qr_code_view_returns_image(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/qr/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_survey_page_shows_view_responses_link(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/")
        self.assertContains(response, "View Responses")
        self.assertContains(response, f"/surveys/{survey.id}/responses/")

    def test_survey_page_shows_export_link(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/")
        self.assertContains(response, "Export to CSV")
        self.assertContains(response, f"/surveys/{survey.id}/export/")


class MySurveysTest(TestCase):
    def test_my_surveys_url_renders_my_surveys_template(self):
        User.objects.create(email="a@b.com")
        response = self.client.get("/surveys/users/a@b.com/")
        self.assertTemplateUsed(response, "my_surveys.html")

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email="wrong@owner.com")
        correct_user = User.objects.create(email="a@b.com")
        response = self.client.get("/surveys/users/a@b.com/")
        self.assertEqual(response.context["owner"], correct_user)


class StudentSurveyViewTest(AuthenticatedTestCase):

    def test_displays_all_questions_for_survey(self):
        survey = self.create_survey()
        Question.objects.create(survey=survey, text="How was the session?")
        Question.objects.create(survey=survey, text="What did you think of capybara?")

        response = self.client.get(f"/survey/{survey.id}/")

        self.assertContains(response, "How was the session?")
        self.assertContains(response, "What did you think of capybara?")

    def test_uses_student_survey_template(self):
        survey = self.create_survey()
        response = self.client.get(f"/survey/{survey.id}/")
        self.assertTemplateUsed(response, "student_survey.html")

    def test_returns_404_for_nonexistent_survey(self):
        response = self.client.get("/survey/999/")
        self.assertEqual(response.status_code, 404)

    def test_displays_form_with_inputs_for_each_question(self):
        survey = self.create_survey()
        q1 = Question.objects.create(survey=survey, text="Question 1")
        q2 = Question.objects.create(survey=survey, text="Question 2")

        response = self.client.get(f"/survey/{survey.id}/")

        self.assertContains(response, f'name="response_{q1.id}"')
        self.assertContains(response, f'name="response_{q2.id}"')
        self.assertContains(response, 'type="submit"')

    def test_can_save_POST_request_with_answers(self):
        survey = self.create_survey()
        q1 = Question.objects.create(survey=survey, text="Question 1")
        q2 = Question.objects.create(survey=survey, text="Question 2")

        self.client.post(
            f"/survey/{survey.id}/",
            data={
                f"response_{q1.id}": "Answer to question 1",
                f"response_{q2.id}": "Answer to question 2",
            },
        )

        self.assertEqual(Answer.objects.count(), 2)
        answers = Answer.objects.all()
        self.assertEqual(answers[0].answer_text, "Answer to question 1")
        self.assertEqual(answers[1].answer_text, "Answer to question 2")

    def test_displays_confirmation_after_successful_submission(self):
        survey = self.create_survey()
        q1 = Question.objects.create(survey=survey, text="Question 1")

        response = self.client.post(
            f"/survey/{survey.id}/",
            data={
                f"response_{q1.id}": "My answer",
            },
        )

        self.assertContains(response, "Thank you")
        self.assertContains(response, "confirmation-message")


class ExportResponsesTest(AuthenticatedTestCase):
    # setUp inherited from AuthenticatedTestCase

    def test_export_url_exists(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/export/")
        self.assertEqual(response.status_code, 200)

    def test_export_returns_csv_file(self):
        survey = self.create_survey()
        response = self.client.get(f"/surveys/{survey.id}/export/")

        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=", response["Content-Disposition"])

    def test_export_includes_question_headers(self):
        survey = self.create_survey()
        q1 = Question.objects.create(
            survey=survey, text="Question 1", question_type="text"
        )
        q2 = Question.objects.create(
            survey=survey, text="Question 2", question_type="rating", options=[1, 2, 3]
        )

        response = self.client.get(f"/surveys/{survey.id}/export/")
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        header = next(csv_reader)

        self.assertIn("Question 1", header)
        self.assertIn("Question 2", header)

    def test_export_includes_answer_data(self):
        survey = self.create_survey()
        q1 = Question.objects.create(
            survey=survey, text="Question 1", question_type="text"
        )
        q2 = Question.objects.create(
            survey=survey, text="Question 2", question_type="text"
        )

        # Create a submission with answers
        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=q1, answer_text="Answer 1A", submission=submission
        )
        Answer.objects.create(
            question=q2, answer_text="Answer 2A", submission=submission
        )

        response = self.client.get(f"/surveys/{survey.id}/export/")
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)

        self.assertEqual(len(rows), 2)  # Header + 1 data row
        self.assertEqual(
            rows[0], ["Submission ID", "Question 1", "Question 2"]
        )  # Header
        self.assertEqual(rows[1], ["1", "Answer 1A", "Answer 2A"])  # Data

    def test_export_with_no_submissions_only_shows_header(self):
        survey = self.create_survey()
        q1 = Question.objects.create(
            survey=survey, text="Question 1", question_type="text"
        )

        response = self.client.get(f"/surveys/{survey.id}/export/")
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)

        self.assertEqual(len(rows), 1)  # Only header row
        self.assertEqual(rows[0], ["Submission ID", "Question 1"])
