from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from surveys.models import Survey, Question, Submission, Answer


class StudentSurveyViewTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.survey = Survey.objects.create(owner=self.instructor, name="Test Survey")
        self.question = Question.objects.create(survey=self.survey, text="How was it?")

    def test_student_can_access_survey_without_login(self):
        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_survey_view_uses_correct_template(self):
        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )
        self.assertTemplateUsed(response, "student_survey.html")

    def test_survey_view_shows_survey_name(self):
        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )
        self.assertContains(response, "Test Survey")

    def test_survey_view_shows_questions(self):
        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )
        self.assertContains(response, "How was it?")

    def test_survey_view_displays_form_inputs_for_questions(self):
        q1 = Question.objects.create(survey=self.survey, text="Question 1")
        q2 = Question.objects.create(survey=self.survey, text="Question 2")

        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )

        self.assertContains(response, f'name="response_{q1.id}"')
        self.assertContains(response, f'name="response_{q2.id}"')
        self.assertContains(response, 'type="submit"')

    def test_survey_view_404_for_nonexistent_survey(self):
        response = self.client.get(reverse("students:take_survey", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_post_creates_submission_with_answers(self):
        response = self.client.post(
            reverse("students:take_survey", args=[self.survey.id]),
            {f"response_{self.question.id}": "It was great!"},
        )

        self.assertEqual(Submission.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 1)

        answer = Answer.objects.first()
        self.assertEqual(answer.answer_text, "It was great!")
        self.assertEqual(answer.question, self.question)

    def test_post_shows_confirmation(self):
        response = self.client.post(
            reverse("students:take_survey", args=[self.survey.id]),
            {f"response_{self.question.id}": "Great!"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thank you")


class QuestionTypeRenderingTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="testpass123"
        )
        self.survey = Survey.objects.create(owner=self.instructor, name="Test Survey")
        self.question = Question.objects.create(survey=self.survey, text="How was it?")

    def test_survey_displays_multiple_choice_as_radio_buttons(self):
        question = Question.objects.create(
            survey=self.survey,
            text="How would you rate this?",
            question_type="multiple_choice",
            options=["Excellent", "Good", "Fair", "Poor"],
        )

        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )

        # Should have radio inputs with correct values
        self.assertContains(response, 'type="radio"')
        self.assertContains(response, 'value="Excellent"')
        self.assertContains(response, 'value="Good"')
        self.assertContains(response, 'value="Fair"')
        self.assertContains(response, 'value="Poor"')
        # All radios should have the same name (for the question)
        self.assertContains(response, f'name="response_{question.id}"', count=4)

    def test_survey_displays_yes_no_as_radio_buttons(self):
        question = Question.objects.create(
            survey=self.survey,
            text="Did you enjoy this?",
            question_type="yes_no",
            options=["Yes", "No"],  # Add this!
        )

        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )

        # Should have radio inputs for Yes and No
        self.assertContains(response, 'type="radio"')
        self.assertContains(response, 'value="Yes"')
        self.assertContains(response, 'value="No"')
        self.assertContains(response, f'name="response_{question.id}"', count=2)

    def test_survey_displays_rating_scale_as_radio_buttons(self):
        question = Question.objects.create(
            survey=self.survey,
            text="Rate from 1-5",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )

        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )

        # Should have radio inputs for each rating
        self.assertContains(response, 'type="radio"')
        self.assertContains(response, 'value="1"')
        self.assertContains(response, 'value="5"')
        self.assertContains(response, f'name="response_{question.id}"', count=5)

    def test_survey_displays_checkbox_questions_as_checkboxes(self):
        question = Question.objects.create(
            survey=self.survey,
            text="Select all that apply",
            question_type="checkbox",
            options=["Python", "Django", "Testing"],
        )

        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )

        # Should have checkbox inputs
        self.assertContains(response, 'type="checkbox"')
        self.assertContains(response, 'value="Python"')
        self.assertContains(response, 'value="Django"')
        self.assertContains(response, 'value="Testing"')
        # Checkboxes need array-style names for multiple selections
        self.assertContains(response, f'name="response_{question.id}"', count=3)

    def test_comment_boxes_appear_for_non_text_questions(self):
        # Text question - no comment box
        text_q = Question.objects.create(
            survey=self.survey, text="Text question", question_type="text"
        )

        # Multiple choice - should have comment box
        mc_q = Question.objects.create(
            survey=self.survey,
            text="MC question",
            question_type="multiple_choice",
            options=["A", "B"],
        )

        response = self.client.get(
            reverse("students:take_survey", args=[self.survey.id])
        )

        # Text question should NOT have comment field
        self.assertNotContains(response, f'name="comment_{text_q.id}"')

        # Multiple choice SHOULD have comment field
        self.assertContains(response, f'name="comment_{mc_q.id}"')
