from django.test import TestCase
from surveys.models import Question, Survey


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")

        self.assertTemplateUsed(response, "home.html")

    def test_renders_input_form(self):
        response = self.client.get("/")

        self.assertContains(response, '<form method="POST" action="/surveys/new">')
        self.assertContains(response, '<input name="question_text"')


class NewQuestionTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_survey(self):
        other_survey = Survey.objects.create()
        correct_survey = Survey.objects.create()

        self.client.post(
            f"/surveys/{correct_survey.id}/add_question",
            data={"question_text": "A new question for an existing survey"},
        )

        self.assertEqual(Question.objects.count(), 1)
        new_question = Question.objects.get()
        self.assertEqual(new_question.text, "A new question for an existing survey")
        self.assertEqual(new_question.survey, correct_survey)

    def test_redirects_after_POST(self):
        other_survey = Survey.objects.create()
        correct_survey = Survey.objects.create()

        response = self.client.post(
            f"/surveys/{correct_survey.id}/add_question",
            data={"question_text": "A new question for an existing survey"},
        )

        self.assertRedirects(response, f"/surveys/{correct_survey.id}/")


class SurveyViewTest(TestCase):
    def test_uses_question_template(self):
        mysurvey = Survey.objects.create()
        response = self.client.get(f"/surveys/{mysurvey.id}/")

        self.assertTemplateUsed(response, "survey.html")

    def test_renders_input_form(self):
        mysurvey = Survey.objects.create()
        response = self.client.get(f"/surveys/{mysurvey.id}/")

        self.assertContains(response, '<form method="POST" action="/surveys/new">')
        self.assertContains(response, '<input name="question_text"')

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
