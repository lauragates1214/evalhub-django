from django.test import TestCase
from surveys.models import Survey


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")

        self.assertTemplateUsed(response, "home.html")

    def test_renders_input_form(self):
        response = self.client.get("/")

        self.assertContains(response, '<form method="POST" action="/">')
        self.assertContains(response, '<input name="survey_text"')

    def test_can_save_a_POST_request(self):
        self.client.post("/", data={"survey_text": "A new survey"})

        new_survey = Survey.objects.first()
        self.assertEqual(Survey.objects.count(), 1)
        self.assertEqual(new_survey.text, "A new survey")

    def test_redirects_after_POST(self):
        response = self.client.post("/", data={"survey_text": "A new survey"})

        self.assertRedirects(response, "/surveys/the-only-survey-in-the-world/")

    def test_only_saves_items_when_necessary(self):
        self.client.get("/")

        self.assertEqual(Survey.objects.count(), 0)


class SurveyViewTest(TestCase):
    def test_uses_survey_template(self):
        response = self.client.get("/surveys/the-only-survey-in-the-world/")
        self.assertTemplateUsed(response, "survey.html")

    def test_renders_input_form(self):
        response = self.client.get("/surveys/the-only-survey-in-the-world/")

        self.assertContains(response, '<form method="POST" action="/">')
        self.assertContains(response, '<input name="survey_text"')

    def test_displays_all_surveys(self):
        Survey.objects.create(text="Survey 1")
        Survey.objects.create(text="Survey 2")

        response = self.client.get("/surveys/the-only-survey-in-the-world/")

        self.assertContains(response, "Survey 1")
        self.assertContains(response, "Survey 2")
