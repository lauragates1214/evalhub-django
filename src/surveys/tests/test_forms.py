from django import forms
from django.test import TestCase

from tests.base import AuthenticatedTestCase
from accounts.models import User

from surveys.forms import (
    DUPLICATE_QUESTION_ERROR,
    EMPTY_QUESTION_ERROR,
    QuestionForm,
    SurveyAnswerForm,
)
from surveys.models import Answer, Question, Submission, Survey


class QuestionFormTest(TestCase):
    def test_form_validation_for_blank_questions(self):
        form = QuestionForm(data={"text": ""})

        self.assertFalse(
            form.is_valid()
        )  # api for checking form validation before trying to save
        self.assertEqual(form.errors["text"], [EMPTY_QUESTION_ERROR])

    def test_form_save_handles_saving_to_a_survey(self):
        survey = Survey.objects.create()
        form = QuestionForm(data={"text": "save me"})
        form.is_valid()  # must call before accessing cleaned_data
        new_question = form.save(for_survey=survey)

        self.assertEqual(
            new_question, Question.objects.get()
        )  # there is now one and only one Question in the DB
        self.assertEqual(new_question.text, "save me")
        self.assertEqual(new_question.survey, survey)

    def test_form_can_be_initialized_with_survey(self):
        survey = Survey.objects.create()
        form = QuestionForm(for_survey=survey, data={"text": "test question"})
        self.assertTrue(form.is_valid())

        new_question = form.save()
        self.assertEqual(new_question.survey, survey)

    def test_form_validation_for_duplicate_questions(self):
        survey = Survey.objects.create()
        Question.objects.create(survey=survey, text="no twins!")
        form = QuestionForm(for_survey=survey, data={"text": "no twins!"})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["text"], [DUPLICATE_QUESTION_ERROR])


class SurveyAnswerFormTest(AuthenticatedTestCase):
    # setUp inherited from AuthenticatedTestCase

    def test_form_has_field_for_each_question(self):
        survey = self.create_survey()
        q1 = Question.objects.create(survey=survey, text="Question 1")
        q2 = Question.objects.create(survey=survey, text="Question 2")

        form = SurveyAnswerForm(survey=survey)

        self.assertIn(f"response_{q1.id}", form.fields)
        self.assertIn(f"response_{q2.id}", form.fields)

    def test_form_saves_answers_for_each_question(self):
        survey = self.create_survey()
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

    def test_form_renders_radio_buttons_for_multiple_choice(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Rate this course",
            question_type="multiple_choice",
            options=["Excellent", "Good", "Fair", "Poor"],
        )

        form = SurveyAnswerForm(survey=survey)

        form_html = form.as_p()
        self.assertIn('type="radio"', form_html)
        self.assertIn('value="Excellent"', form_html)
        self.assertIn('value="Good"', form_html)

    def test_form_includes_comment_field_for_multiple_choice(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Rate this course",
            question_type="multiple_choice",
            options=["Excellent", "Good", "Fair", "Poor"],
        )

        form = SurveyAnswerForm(survey=survey)

        self.assertIn(f"comment_{question.id}", form.fields)
        self.assertIsInstance(form.fields[f"comment_{question.id}"], forms.CharField)

    def test_form_saves_comment_with_answer(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Rate this course",
            question_type="multiple_choice",
            options=["Excellent", "Good"],
        )

        form = SurveyAnswerForm(
            survey=survey,
            data={
                f"response_{question.id}": "Excellent",
                f"comment_{question.id}": "Great capybara!",
            },
        )

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(Answer.objects.count(), 1)
        answer = Answer.objects.first()
        self.assertEqual(answer.answer_text, "Excellent")
        self.assertEqual(answer.comment_text, "Great capybara!")

    def test_form_renders_radio_buttons_for_rating_scale(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Rate capybara",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )

        form = SurveyAnswerForm(survey=survey)

        form_html = form.as_p()
        self.assertIn('type="radio"', form_html)
        self.assertIn('value="5"', form_html)

    def test_form_renders_checkboxes_for_checkbox_question(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Which topics interested you?",
            question_type="checkbox",
            options=["Capybara", "Capybaras", "Cap"],
        )

        form = SurveyAnswerForm(survey=survey)

        form_html = form.as_p()
        self.assertIn('type="checkbox"', form_html)
        self.assertIn('value="Capybara"', form_html)
        self.assertIn('value="Capybaras"', form_html)

    def test_form_renders_radio_buttons_for_yes_no_question(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Would you capybara?",
            question_type="yes_no",
            options=["Yes", "No"],
        )

        form = SurveyAnswerForm(survey=survey)

        form_html = form.as_p()
        self.assertIn('type="radio"', form_html)
        self.assertIn('value="Yes"', form_html)
        self.assertIn('value="No"', form_html)

    def test_form_creates_submission_when_saving(self):
        survey = self.create_survey()
        q1 = Question.objects.create(
            survey=survey, text="Question 1", question_type="text"
        )

        form = SurveyAnswerForm(survey=survey, data={f"response_{q1.id}": "Answer 1"})

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.first()
        self.assertEqual(submission.survey, survey)
        self.assertEqual(submission.answers.count(), 1)

    def test_form_saves_multiple_checkbox_selections(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Which topics interested you?",
            question_type="checkbox",
            options=["Python", "Django", "Testing", "Deployment"],
        )

        form = SurveyAnswerForm(
            survey=survey,
            data={
                f"response_{question.id}": ["Python", "Django", "Testing"],
            },
        )

        self.assertTrue(form.is_valid())
        form.save()

        answer = Answer.objects.first()
        # Checkbox answers should be stored as comma-separated or list format
        # Adjust assertion based on how your model handles multiple selections
        self.assertIn("Python", answer.answer_text)
        self.assertIn("Django", answer.answer_text)
        self.assertIn("Testing", answer.answer_text)

    def test_form_with_empty_survey(self):
        survey = self.create_survey()

        form = SurveyAnswerForm(survey=survey)

        # Form with no fields should have no fields to validate
        self.assertEqual(len(form.fields), 0)

        # When submitting empty data, form should still be valid
        form = SurveyAnswerForm(survey=survey, data={})
        self.assertTrue(form.is_valid())

        # Should create submission but no answers
        form.save()
        self.assertEqual(Submission.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 0)

    def test_form_handles_mixed_question_types(self):
        survey = self.create_survey()

        text_q = Question.objects.create(
            survey=survey, text="Name", question_type="text"
        )

        rating_q = Question.objects.create(
            survey=survey,
            text="Rate the course",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )

        checkbox_q = Question.objects.create(
            survey=survey,
            text="Select topics",
            question_type="checkbox",
            options=["Topic A", "Topic B"],
        )

        form = SurveyAnswerForm(
            survey=survey,
            data={
                f"response_{text_q.id}": "John Doe",
                f"response_{rating_q.id}": "4",
                f"response_{checkbox_q.id}": ["Topic A"],
                f"comment_{rating_q.id}": "Good course",
            },
        )

        self.assertTrue(form.is_valid())
        form.save()

        # Check all answers were saved correctly
        self.assertEqual(Answer.objects.count(), 3)

        text_answer = Answer.objects.get(question=text_q)
        self.assertEqual(text_answer.answer_text, "John Doe")

        rating_answer = Answer.objects.get(question=rating_q)
        self.assertEqual(rating_answer.answer_text, "4")
        self.assertEqual(rating_answer.comment_text, "Good course")

        checkbox_answer = Answer.objects.get(question=checkbox_q)
        self.assertIn("Topic A", checkbox_answer.answer_text)

    def test_form_validates_required_fields_when_configured(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Required question",
            question_type="text",
            # Assuming there might be a 'required' field in future
        )

        form = SurveyAnswerForm(
            survey=survey,
            data={f"response_{question.id}": ""},
        )

        # Currently all fields are optional (required=False)
        # This test documents current behaviour
        self.assertTrue(form.is_valid())

        # If implement required fields later, update this test

    def test_form_handles_special_characters_in_answers(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey, text="Feedback", question_type="text"
        )

        special_text = "Test with 'quotes' and \"double quotes\" & symbols < > /"

        form = SurveyAnswerForm(
            survey=survey,
            data={f"response_{question.id}": special_text},
        )

        self.assertTrue(form.is_valid())
        form.save()

        answer = Answer.objects.first()
        self.assertEqual(answer.answer_text, special_text)
