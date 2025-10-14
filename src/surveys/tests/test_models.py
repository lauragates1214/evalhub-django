from django.core.exceptions import (
    ValidationError,
)  # for model-level validation, full_clean()
from django.db import IntegrityError  # for DB-level validation, save()

from tests.base import AuthenticatedTestCase
from accounts.models import User
from surveys.models import Answer, Question, Submission, Survey


class AnswerModelTest(AuthenticatedTestCase):
    def test_can_save_response_to_question(self):
        survey = self.create_survey()
        question = Question.objects.create(survey=survey, text="How was it?")
        submission = Submission.objects.create(survey=survey)

        answer = Answer.objects.create(
            question=question, answer_text="It was great!", submission=submission
        )

        self.assertEqual(answer.question, question)
        self.assertEqual(answer.answer_text, "It was great!")

    def test_answer_can_have_optional_comment(self):
        survey = self.create_survey()
        question = Question.objects.create(survey=survey, text="How was it?")
        submission = Submission.objects.create(survey=survey)

        answer = Answer.objects.create(
            question=question,
            answer_text="It was great!",
            comment_text="Especially the capybara",
            submission=submission,
        )

        self.assertEqual(answer.comment_text, "Especially the capybara")

    def test_answer_comment_can_be_blank(self):
        survey = self.create_survey()
        question = Question.objects.create(survey=survey, text="How was it?")
        submission = Submission.objects.create(survey=survey)

        answer = Answer.objects.create(
            question=question, answer_text="Good", submission=submission
        )

        self.assertEqual(answer.comment_text, "")

    def test_answer_related_name_on_submission(self):
        survey = self.create_survey()
        question = Question.objects.create(survey=survey, text="Q1")
        submission = Submission.objects.create(survey=survey)

        answer1 = Answer.objects.create(
            question=question, answer_text="Answer 1", submission=submission
        )
        answer2 = Answer.objects.create(
            question=question, answer_text="Answer 2", submission=submission
        )

        self.assertEqual(submission.answers.count(), 2)
        self.assertIn(answer1, submission.answers.all())
        self.assertIn(answer2, submission.answers.all())


class QuestionModelsTest(AuthenticatedTestCase):
    # setUp inherited from AuthenticatedTestCase

    def test_default_text(self):
        question = Question()
        self.assertEqual(question.text, "")

    def test_question_is_related_to_survey(self):
        survey = self.create_survey()
        question = Question()
        question.survey = survey
        question.save()

        self.assertIn(question, survey.question_set.all())

    def test_cannot_save_null_questions(self):
        survey = self.create_survey()
        question = Question(survey=survey, text=None)

        with self.assertRaises(IntegrityError):
            question.save()  # database-level validation

    def test_cannot_save_empty_questions(self):
        survey = self.create_survey()
        question = Question(survey=survey, text="")

        with self.assertRaises(ValidationError):
            question.full_clean()  # model-level validation

    def test_duplicate_questions_are_invalid(self):
        survey = self.create_survey()
        Question.objects.create(survey=survey, text="why")

        with self.assertRaises(ValidationError):
            question = Question(survey=survey, text="why")
            question.full_clean()  # model-level validation

    # TODO: when expand, remove this test as will have org-wide question bank
    def test_CAN_save_same_question_to_different_surveys(self):
        survey1 = self.create_survey()
        survey2 = self.create_survey()
        Question.objects.create(survey=survey1, text="why")
        question = Question(survey=survey2, text="why")

        question.full_clean()  # should not raise

    def test_question_type_defaults_to_text(self):
        survey = self.create_survey()
        question = Question.objects.create(survey=survey, text="A question")

        self.assertEqual(question.question_type, "text")

    def test_can_create_multiple_choice_question_with_options(self):
        survey = self.create_survey()
        question = Question.objects.create(
            survey=survey,
            text="Rate this course",
            question_type="multiple_choice",
            options=["Excellent", "Good", "Fair", "Poor"],
        )

        self.assertEqual(question.question_type, "multiple_choice")
        self.assertEqual(question.options, ["Excellent", "Good", "Fair", "Poor"])

    def test_question_options_field_for_different_types(self):
        survey = self.create_survey()

        # Test that options can be None for text questions
        text_q = Question.objects.create(
            survey=survey, text="Text question", question_type="text", options=None
        )
        self.assertIsNone(text_q.options)

        # Test rating options as integers
        rating_q = Question.objects.create(
            survey=survey,
            text="Rating question",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )
        self.assertEqual(rating_q.options, [1, 2, 3, 4, 5])

        # Test yes/no options
        yes_no_q = Question.objects.create(
            survey=survey,
            text="Yes/No question",
            question_type="yes_no",
            options=["Yes", "No"],
        )
        self.assertEqual(yes_no_q.options, ["Yes", "No"])


class SubmissionModelTest(AuthenticatedTestCase):

    def test_can_create_submission(self):
        survey = self.create_survey()
        submission = Submission.objects.create(survey=survey)

        self.assertEqual(submission.survey, survey)

    def test_answers_can_be_linked_to_submission(self):
        survey = self.create_survey()
        question = Question.objects.create(survey=survey, text="Q1")
        submission = Submission.objects.create(survey=survey)
        answer = Answer.objects.create(
            question=question, answer_text="Answer", submission=submission
        )

        self.assertEqual(answer.submission, submission)

    def test_submission_has_created_at_timestamp(self):
        from django.utils import timezone

        survey = self.create_survey()
        before = timezone.now()
        submission = Submission.objects.create(survey=survey)
        after = timezone.now()

        self.assertGreaterEqual(submission.created_at, before)
        self.assertLessEqual(submission.created_at, after)

    def test_submission_related_name_on_survey(self):
        survey = self.create_survey()
        submission1 = Submission.objects.create(survey=survey)
        submission2 = Submission.objects.create(survey=survey)

        self.assertEqual(survey.submissions.count(), 2)
        self.assertIn(submission1, survey.submissions.all())
        self.assertIn(submission2, survey.submissions.all())

    def test_cascade_delete_submission_deletes_answers(self):
        survey = self.create_survey()
        question = Question.objects.create(survey=survey, text="Q1")
        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=question, answer_text="Answer", submission=submission
        )

        self.assertEqual(Answer.objects.count(), 1)

        submission.delete()

        self.assertEqual(Answer.objects.count(), 0)


class SurveyModelTest(AuthenticatedTestCase):
    # setUp inherited from AuthenticatedTestCase

    def test_get_absolute_url(self):
        survey = self.create_survey()
        self.assertEqual(survey.get_absolute_url(), f"/instructor/surveys/{survey.id}/")

    def test_survey_questions_order(self):
        survey = self.create_survey()
        question1 = Question.objects.create(survey=survey, text="i1")
        question2 = Question.objects.create(survey=survey, text="question 2")
        question3 = Question.objects.create(survey=survey, text="3")

        self.assertEqual(
            list(
                survey.question_set.all()
            ),  # list() to force evaluation of the queryset
            [
                question1,
                question2,
                question3,
            ],  # checks ordering by id as in Meta class of Question model
        )

    def test_surveys_can_have_owners(self):
        user = self.create_user("a@b.com")
        survey = Survey.objects.create(owner=user)
        self.assertIn(survey, user.surveys.all())

    def test_string_representation(self):
        question = Question(text="some text")
        self.assertEqual(str(question), "some text")

    def test_survey_can_have_a_name(self):
        survey = Survey.objects.create(owner=self.user, name="My Survey")
        self.assertEqual(survey.name, "My Survey")

    def test_survey_can_generate_qr_code_url(self):
        instructor = self.create_user("instructor@test.com")
        survey = Survey.objects.create(owner=instructor)

        qr_code_url = survey.get_qr_code_url()

        self.assertIn("/survey/", qr_code_url)
        self.assertIn(str(survey.id), qr_code_url)

    def test_survey_has_text_field(self):
        survey = Survey.objects.create(
            owner=self.user,
            name="Test Survey",
            text="Welcome to this survey about capybaras",
        )
        self.assertEqual(survey.text, "Welcome to this survey about capybaras")

    def test_survey_has_created_at_timestamp(self):
        from django.utils import timezone

        before = timezone.now()
        survey = Survey.objects.create(owner=self.user)
        after = timezone.now()

        self.assertGreaterEqual(survey.created_at, before)
        self.assertLessEqual(survey.created_at, after)

    def test_cascade_delete_survey_deletes_questions(self):
        survey = self.create_survey()
        Question.objects.create(survey=survey, text="Q1")
        Question.objects.create(survey=survey, text="Q2")

        self.assertEqual(Question.objects.count(), 2)

        survey.delete()

        self.assertEqual(Question.objects.count(), 0)

    def test_cascade_delete_survey_deletes_submissions(self):
        survey = self.create_survey()
        Submission.objects.create(survey=survey)
        Submission.objects.create(survey=survey)

        self.assertEqual(Submission.objects.count(), 2)

        survey.delete()

        self.assertEqual(Submission.objects.count(), 0)
