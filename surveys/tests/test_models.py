from django.test import TestCase
from surveys.models import Survey


class SurveyModelTest(TestCase):
    def test_saving_and_retrieving_surveys(self):
        first_survey = Survey()
        first_survey.text = "The first (ever) survey"
        first_survey.save()

        second_survey = Survey()
        second_survey.text = "Survey the second"
        second_survey.save()

        saved_surveys = Survey.objects.all()
        first_saved_survey = saved_surveys[0]
        second_saved_survey = saved_surveys[1]

        self.assertEqual(saved_surveys.count(), 2)
        self.assertEqual(first_saved_survey.text, "The first (ever) survey")
        self.assertEqual(second_saved_survey.text, "Survey the second")
