from django.test import TestCase

from surveys.forms import EMPTY_QUESTION_ERROR, QuestionForm


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
