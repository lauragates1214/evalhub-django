from django.core.exceptions import (
    ValidationError,
)  # for model-level validation, full_clean()
from django.db import IntegrityError  # for DB-level validation, save()
from django.test import TestCase

from surveys.models import Question, Survey


class QuestionModelsTest(TestCase):
    def test_default_text(self):
        question = Question()
        self.assertEqual(question.text, "")

    def test_question_is_related_to_survey(self):
        mysurvey = Survey.objects.create()
        question = Question()
        question.survey = mysurvey
        question.save()
        self.assertIn(question, mysurvey.question_set.all())

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

    def test_duplicate_questions_are_invalid(self):
        mysurvey = Survey.objects.create()
        Question.objects.create(survey=mysurvey, text="why")
        with self.assertRaises(ValidationError):
            question = Question(survey=mysurvey, text="why")
            question.full_clean()  # model-level validation

    # TODO: when expand, remove this test as will have org-wide question bank
    def test_CAN_save_same_question_to_different_surveys(self):
        survey1 = Survey.objects.create()
        survey2 = Survey.objects.create()
        Question.objects.create(survey=survey1, text="why")
        question = Question(survey=survey2, text="why")
        question.full_clean()  # should not raise


class SurveyModelTest(TestCase):
    def test_get_absolute_url(self):
        mysurvey = Survey.objects.create()

        self.assertEqual(mysurvey.get_absolute_url(), f"/surveys/{mysurvey.id}/")

    def test_survey_questions_order(self):
        survey1 = Survey.objects.create()
        question1 = Question.objects.create(survey=survey1, text="i1")
        question2 = Question.objects.create(survey=survey1, text="question 2")
        question3 = Question.objects.create(survey=survey1, text="3")
        self.assertEqual(
            list(
                survey1.question_set.all()
            ),  # list() to force evaluation of the queryset
            [
                question1,
                question2,
                question3,
            ],  # checks ordering by id as in Meta class of Question model
        )

    def test_string_representation(self):
        question = Question(text="some text")
        self.assertEqual(str(question), "some text")
