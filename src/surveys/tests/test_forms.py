from django.test import TestCase

from surveys.forms import (
    DUPLICATE_QUESTION_ERROR,
    EMPTY_QUESTION_ERROR,
    ExistingSurveyQuestionForm,
    QuestionForm,
)
from surveys.models import Question, Survey


class QuestionFormTest(TestCase):
    def test_form_validation_for_blank_questions(self):
        form = QuestionForm(data={"text": ""})

        self.assertFalse(
            form.is_valid()
        )  # api for checking form validation before trying to save
        self.assertEqual(form.errors["text"], [EMPTY_QUESTION_ERROR])

    def test_form_save_handles_saving_to_a_survey(self):
        mysurvey = Survey.objects.create()
        form = QuestionForm(data={"text": "save me"})
        form.is_valid()  # must call before accessing cleaned_data
        new_question = form.save(for_survey=mysurvey)

        self.assertEqual(
            new_question, Question.objects.get()
        )  # there is now one and only one Question in the DB
        self.assertEqual(new_question.text, "save me")
        self.assertEqual(new_question.survey, mysurvey)


class ExistingSurveyQuestionFormTest(TestCase):
    def test_form_validation_for_blank_questions(self):
        survey = Survey.objects.create()
        form = ExistingSurveyQuestionForm(for_survey=survey, data={"text": ""})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["text"], [EMPTY_QUESTION_ERROR])

    def test_form_validation_for_duplicate_questions(self):
        survey = Survey.objects.create()
        Question.objects.create(survey=survey, text="no twins!")
        form = ExistingSurveyQuestionForm(for_survey=survey, data={"text": "no twins!"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["text"], [DUPLICATE_QUESTION_ERROR])

    def test_form_save(self):
        mysurvey = Survey.objects.create()
        form = ExistingSurveyQuestionForm(for_survey=mysurvey, data={"text": "hi"})
        self.assertTrue(form.is_valid())

        new_question = (
            form.save()
        )  # should not require arguments as already associated with survey in constructor
        self.assertEqual(new_question, Question.objects.get())
