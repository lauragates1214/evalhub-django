from django.test import TestCase

from accounts.models import User

from surveys.forms import (
    DUPLICATE_QUESTION_ERROR,
    EMPTY_QUESTION_ERROR,
    ExistingSurveyQuestionForm,
    QuestionForm,
    SurveyAnswerForm,
)
from surveys.models import Answer, Question, Survey


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


class SurveyAnswerFormTest(TestCase):
    def test_form_has_field_for_each_question(self):
        instructor = User.objects.create(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        q1 = Question.objects.create(survey=survey, text="Question 1")
        q2 = Question.objects.create(survey=survey, text="Question 2")

        form = SurveyAnswerForm(survey=survey)

        self.assertIn(f"response_{q1.id}", form.fields)
        self.assertIn(f"response_{q2.id}", form.fields)

    def test_form_saves_answers_for_each_question(self):
        instructor = User.objects.create(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        q1 = Question.objects.create(survey=survey, text="Question 1")
        q2 = Question.objects.create(survey=survey, text="Question 2")

        form = SurveyAnswerForm(
            survey=survey,
            data={
                f"response_{q1.id}": "Answer 1",
                f"response_{q2.id}": "Answer 2",
            },
        )

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(Answer.objects.count(), 2)
        self.assertEqual(
            Answer.objects.filter(question=q1).first().answer_text, "Answer 1"
        )
        self.assertEqual(
            Answer.objects.filter(question=q2).first().answer_text, "Answer 2"
        )
