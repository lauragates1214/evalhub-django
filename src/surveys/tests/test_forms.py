from django.test import TestCase

from surveys.forms import EMPTY_QUESTION_ERROR, QuestionForm
from surveys.models import Question, Survey


class QuestionFormTest(TestCase):
    def test_form_question_input_has_placeholder_and_css_classes(self):
        form = QuestionForm()

        rendered = form.as_p()

        self.assertIn('placeholder="Enter a question"', rendered)
        self.assertIn('class="form-control form-control-lg"', rendered)

    def test_form_validation_for_blank_items(self):
        form = QuestionForm(data={"text": ""})

        self.assertFalse(
            form.is_valid()
        )  # api for checking form validation before trying to save
        self.assertEqual(form.errors["text"], [EMPTY_QUESTION_ERROR])

    def test_form_save_handles_saving_to_a_survey(self):
        mysurvey = Survey.objects.create()
        form = QuestionForm(data={"text": "save me"})
        new_question = form.save(for_survey=mysurvey)

        self.assertEqual(
            new_question, Question.objects.get()
        )  # there is now one and only one Question in the DB
        self.assertEqual(new_question.text, "save me")
        self.assertEqual(new_question.survey, mysurvey)
