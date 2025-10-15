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
