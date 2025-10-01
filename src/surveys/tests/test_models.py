from django.core.exceptions import (
    ValidationError,
)  # for model-level validation, full_clean()
from django.db import IntegrityError  # for DB-level validation, save()
from django.test import TestCase

from surveys.models import Question, Survey


class SurveyAndQuestionModelsTest(TestCase):
    def test_saving_and_retrieving_questions(self):
        mysurvey = Survey()
        mysurvey.save()

        first_question = Question()
        first_question.text = "The first (ever) survey question"
        first_question.survey = mysurvey
        first_question.save()

        second_question = Question()
        second_question.text = "Question the second"
        second_question.survey = mysurvey
        second_question.save()

        saved_survey = Survey.objects.get()
        self.assertEqual(saved_survey, mysurvey)

        saved_questions = Question.objects.all()
        self.assertEqual(saved_questions.count(), 2)

        first_saved_question = saved_questions[0]
        second_saved_question = saved_questions[1]
        self.assertEqual(first_saved_question.text, "The first (ever) survey question")
        self.assertEqual(first_saved_question.survey, mysurvey)
        self.assertEqual(second_saved_question.text, "Question the second")
        self.assertEqual(second_saved_question.survey, mysurvey)

    def test_cannot_save_null_questions(self):
        mysurvey = Survey.objects.create()
        question = Question(survey=mysurvey, text=None)
        with self.assertRaises(IntegrityError):
            question.save()  # database-level validation

    def test_cannot_save_empty_questions(self):
        mysurvey = Survey.objects.create()
        question = Question(survey=mysurvey, text="")
        with self.assertRaises(ValidationError):
            question.full_clean()  # model-level validation

    def test_get_absolute_url(self):
        mysurvey = Survey.objects.create()

        self.assertEqual(mysurvey.get_absolute_url(), f"/surveys/{mysurvey.id}/")
