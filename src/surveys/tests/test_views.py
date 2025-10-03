from django.test import TestCase
from django.utils import html

import lxml.html

from unittest import skip

from surveys.forms import (
    DUPLICATE_QUESTION_ERROR,
    EMPTY_QUESTION_ERROR,
)
from surveys.models import Question, Survey


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
