from django.test import TestCase
from surveys.models import Question


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")

        self.assertTemplateUsed(response, "home.html")

    def test_renders_input_form(self):
        response = self.client.get("/")

        self.assertContains(response, '<form method="POST" action="/surveys/new">')
        self.assertContains(response, '<input name="question_text"')


class NewQuestionTest(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post("/surveys/new", data={"question_text": "A new question"})

        new_question = Question.objects.first()
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(new_question.text, "A new question")

    def test_redirects_after_POST(self):
        response = self.client.post(
            "/surveys/new", data={"question_text": "A new question"}
        )

        self.assertRedirects(response, "/surveys/the-only-survey-in-the-world/")


class QuestionViewTest(TestCase):
    def test_uses_question_template(self):
        response = self.client.get("/surveys/the-only-survey-in-the-world/")

        self.assertTemplateUsed(response, "survey.html")

    def test_renders_input_form(self):
        response = self.client.get("/surveys/the-only-survey-in-the-world/")

        self.assertContains(response, '<form method="POST" action="/surveys/new">')
        self.assertContains(response, '<input name="question_text"')

    def test_displays_all_questions(self):
        Question.objects.create(text="Question 1")
        Question.objects.create(text="Question 2")

        response = self.client.get("/surveys/the-only-survey-in-the-world/")

        self.assertContains(response, "Question 1")
        self.assertContains(response, "Question 2")
