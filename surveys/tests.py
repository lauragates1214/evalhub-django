from django.test import TestCase
from surveys.models import Survey


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_renders_input_form(self):
        response = self.client.get("/")
        self.assertContains(response, '<form method="POST">')
        self.assertContains(response, '<input name="survey_text"')

    def test_can_save_a_POST_request(self):
        response = self.client.post("/", data={"survey_text": "A new survey"})
        self.assertContains(response, "A new survey")
        self.assertTemplateUsed(response, "home.html")


class SurveyModelTest(TestCase):
    def test_saving_and_retrieving_surveys(self):
        first_survey = Survey()
        first_survey.text = "The first (ever) survey"
        first_survey.save()

        second_survey = Survey()
        second_survey.text = "Survey the second"
        second_survey.save()

        saved_surveys = Survey.objects.all()
        self.assertEqual(saved_surveys.count(), 2)

        first_saved_survey = saved_surveys[0]
        second_saved_survey = saved_surveys[1]
        self.assertEqual(first_saved_survey.text, "The first (ever) survey")
        self.assertEqual(second_saved_survey.text, "Survey the second")
