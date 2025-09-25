from django.test import TestCase
from surveys.models import Question


class QuestionModelTest(TestCase):
    def test_saving_and_retrieving_questions(self):
        first_question = Question()
        first_question.text = "The first (ever) question"
        first_question.save()

        second_question = Question()
        second_question.text = "Question the second"
        second_question.save()

        saved_questions = Question.objects.all()
        first_saved_question = saved_questions[0]
        second_saved_question = saved_questions[1]
        self.assertEqual(saved_questions.count(), 2)
        self.assertEqual(first_saved_question.text, "The first (ever) question")
        self.assertEqual(second_saved_question.text, "Question the second")
