from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import html

import lxml.html

from unittest import skip

from surveys.forms import (
    DUPLICATE_QUESTION_ERROR,
    EMPTY_QUESTION_ERROR,
)
from accounts.models import User
from surveys.models import Answer, Question, Survey

User = get_user_model()


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
        parsed = lxml.html.fromstring(
            response.content
        )  # parse HTML into structured object to represent DOM
        [form] = parsed.cssselect(
            "form[method=POST]"
        )  # find form element with method=POST, expect exactly one (hence the brackets)

        self.assertEqual(form.get("action"), "/surveys/new")

        inputs = form.cssselect("input")
        self.assertIn(
            "text", [input.get("name") for input in inputs]
        )  # check at least one input has name=text


class NewSurveyTest(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create(email="test@example.com")
        user.set_password("password")
        user.save()
        self.client.login(username="test@example.com", password="password")

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
        user = User.objects.create(email="a@b.com")
        self.client.force_login(user)
        self.client.post("/surveys/new", data={"text": "new question"})
        new_survey = Survey.objects.get()
        self.assertEqual(new_survey.owner, user)


class SurveyViewTest(TestCase):
    def test_uses_question_template(self):
        mysurvey = Survey.objects.create()
        response = self.client.get(f"/surveys/{mysurvey.id}/")

        self.assertTemplateUsed(response, "survey.html")

    def test_renders_input_form(self):
        mysurvey = Survey.objects.create()
        response = self.client.get(f"/surveys/{mysurvey.id}/")
        parsed = lxml.html.fromstring(
            response.content
        )  # parse HTML into structured object to represent DOM
        [form] = parsed.cssselect(
            "form[method=POST]"
        )  # find form element with method=POST, expect exactly one (hence the brackets)

        self.assertEqual(form.get("action"), f"/surveys/{mysurvey.id}/")

        inputs = form.cssselect("input")
        self.assertIn(
            "text", [input.get("name") for input in inputs]
        )  # check at least one input has name=text

    def test_displays_only_questions_for_that_survey(self):
        correct_survey = Survey.objects.create()
        Question.objects.create(text="Question 1", survey=correct_survey)
        Question.objects.create(text="Question 2", survey=correct_survey)
        other_survey = Survey.objects.create()
        Question.objects.create(text="Other survey question", survey=other_survey)

        response = self.client.get(f"/surveys/{correct_survey.id}/")

        self.assertContains(response, "Question 1")
        self.assertContains(response, "Question 2")
        self.assertNotContains(response, "Other survey question")

    def test_can_save_a_POST_request_to_an_existing_survey(self):
        other_survey = Survey.objects.create()
        correct_survey = Survey.objects.create()

        self.client.post(
            f"/surveys/{correct_survey.id}/",
            data={"text": "A new question for an existing survey"},
        )

        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, "A new question for an existing survey")
        self.assertEqual(new_question.survey, correct_survey)

    def test_POST_redirects_to_survey_view(self):
        other_survey = Survey.objects.create()
        correct_survey = Survey.objects.create()

        response = self.client.post(
            f"/surveys/{correct_survey.id}/",
            data={"text": "A new question for an existing survey"},
        )

        self.assertRedirects(response, f"/surveys/{correct_survey.id}/")

    def post_invalid_input(self):
        mysurvey = Survey.objects.create()
        return self.client.post(f"/surveys/{mysurvey.id}/", data={"text": ""})

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
        parsed = lxml.html.fromstring(response.content)
        [input] = parsed.cssselect("input[name=text]")
        self.assertIn("is-invalid", set(input.classes))

    def test_duplicate_question_validation_errors_end_up_on_surveys_page(self):
        survey1 = Survey.objects.create()
        Question.objects.create(survey=survey1, text="textey")

        response = self.client.post(
            f"/surveys/{survey1.id}/",
            data={"text": "textey"},
        )

        expected_error = html.escape(DUPLICATE_QUESTION_ERROR)
        self.assertContains(response, expected_error)  # check error appears on page
        self.assertTemplateUsed(response, "survey.html")  # check still on survey page
        self.assertEqual(
            Question.objects.all().count(), 1
        )  # check no new question created (haven't saved anything to the DB)

    def test_htmx_request_returns_partial_template(self):
        mysurvey = Survey.objects.create()

        response = self.client.post(
            f"/surveys/{mysurvey.id}/",
            data={"text": "New question"},
            HTTP_HX_REQUEST="true",  # Simulates htmx adding HX-Request header
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/question_list.html")

    def test_htmx_request_includes_new_question_in_response(self):
        mysurvey = Survey.objects.create()

        response = self.client.post(
            f"/surveys/{mysurvey.id}/",
            data={"text": "New question"},
            HTTP_HX_REQUEST="true",
        )

        self.assertContains(response, "New question")
        self.assertEqual(Question.objects.count(), 1)

    def test_non_htmx_request_still_redirects(self):
        mysurvey = Survey.objects.create()

        response = self.client.post(
            f"/surveys/{mysurvey.id}/",
            data={"text": "New question"},
            # No HX-Request header
        )

        self.assertEqual(response.status_code, 302)  # Still redirects for normal forms

    def test_htmx_request_with_invalid_input_returns_partial_template(self):
        mysurvey = Survey.objects.create()
        Question.objects.create(survey=mysurvey, text="duplicate")

        response = self.client.post(
            f"/surveys/{mysurvey.id}/",
            data={"text": "duplicate"},
            HTTP_HX_REQUEST="true",
        )

        self.assertTemplateUsed(response, "partials/question_list.html")
        self.assertContains(response, html.escape(DUPLICATE_QUESTION_ERROR))


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


class StudentSurveyViewTest(TestCase):
    def test_displays_all_questions_for_survey(self):
        instructor = User.objects.create(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        Question.objects.create(survey=survey, text="How was the session?")
        Question.objects.create(survey=survey, text="What did you think of capybara?")

        response = self.client.get(f"/survey/{survey.id}/")

        self.assertContains(response, "How was the session?")
        self.assertContains(response, "What did you think of capybara?")

    def test_uses_student_survey_template(self):
        instructor = User.objects.create(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)

        response = self.client.get(f"/survey/{survey.id}/")

        self.assertTemplateUsed(response, "student_survey.html")

    def test_returns_404_for_nonexistent_survey(self):
        response = self.client.get("/survey/999/")
        self.assertEqual(response.status_code, 404)

    def test_displays_form_with_inputs_for_each_question(self):
        instructor = User.objects.create(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        q1 = Question.objects.create(survey=survey, text="Question 1")
        q2 = Question.objects.create(survey=survey, text="Question 2")

        response = self.client.get(f"/survey/{survey.id}/")

        self.assertContains(response, f'name="response_{q1.id}"')
        self.assertContains(response, f'name="response_{q2.id}"')
        self.assertContains(response, 'type="submit"')

    def test_can_save_POST_request_with_answers(self):
        instructor = User.objects.create(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
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
        instructor = User.objects.create(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        q1 = Question.objects.create(survey=survey, text="Question 1")

        response = self.client.post(
            f"/survey/{survey.id}/",
            data={
                f"response_{q1.id}": "My answer",
            },
        )

        self.assertContains(response, "Thank you")
        self.assertContains(response, "confirmation-message")
