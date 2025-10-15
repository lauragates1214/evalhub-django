from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .base import FunctionalTest
from .pages import StudentSurveyPage

from accounts.models import User
from surveys.models import Survey, Question


class QuestionTypesTest(FunctionalTest):
    def test_student_can_answer_multiple_choice_question(self):
        # Instructor creates a survey with a multiple choice question
        # Create and login the instructor
        self.login("instructor@test.com")

        # Get the user and create the survey with custom question
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        question = Question.objects.create(
            survey=survey,
            text="How would you rate this course?",
            question_type="multiple_choice",
            options=["Excellent", "Good", "Fair", "Poor"],
        )
        self.logout()

        # Student visits the survey
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        # They see radio buttons for the multiple choice question
        survey_page.check_question_exists("How would you rate this course?")

        # They select an option
        survey_page.select_radio_option("Excellent")

        # They can also add an optional comment
        survey_page.add_comment(question.id, "Great instructor!")

        # They submit
        survey_page.submit()

        # They see confirmation
        survey_page.wait_for_confirmation()

    def test_student_can_answer_rating_scale_question(self):
        # Instructor creates a survey with a rating scale question
        self.login("instructor@test.com")
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        question = Question.objects.create(
            survey=survey,
            text="How likely are you to recommend capybara?",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )
        self.logout()

        # Student visits the survey
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        # They see the rating scale question
        survey_page.check_question_exists("How likely are you to recommend capybara?")

        # They select a rating
        survey_page.select_radio_option("5")

        # They add an optional comment
        survey_page.add_comment(question.id, "Best capybara ever!")

        # They submit
        survey_page.submit()

        # They see confirmation
        survey_page.wait_for_confirmation()

    def test_student_can_answer_checkbox_question(self):
        # Instructor creates a survey with a checkbox question
        # Create and login the instructor
        self.login("instructor@test.com")

        # Get the user and create the survey with custom question
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        question = Question.objects.create(
            survey=survey,
            text="Which topics interested you most?",
            question_type="checkbox",
            options=["Capybara", "Capybaras", "Cap", "ybara"],
        )
        self.logout()

        # Student visits the survey
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        # They see checkboxes
        survey_page.check_question_exists("Which topics interested you most?")

        # They select multiple options
        survey_page.select_checkbox_option("Capybara")
        survey_page.select_checkbox_option("Capybaras")

        # They can add a comment
        survey_page.add_comment(question.id, "Looking forward to more cap!")

        # They submit
        survey_page.submit()

        # They see confirmation
        survey_page.wait_for_confirmation()

    def test_student_can_answer_yes_no_question(self):
        # Instructor creates a survey with a yes/no question
        # Create and login the instructor
        self.login("instructor@test.com")

        # Get the user and create the survey with custom question
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        question = Question.objects.create(
            survey=survey,
            text="Would you capybara?",
            question_type="yes_no",
            options=["Yes", "No"],
        )
        self.logout()

        # Student visits the survey
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        # They see radio buttons for yes/no
        survey_page.check_question_exists("Would you capybara?")

        # They select an option
        survey_page.select_radio_option("Yes")

        # They can add a comment
        survey_page.add_comment(question.id, "Definitely!")

        # They submit
        survey_page.submit()

        # They see confirmation
        survey_page.wait_for_confirmation()

    def test_comment_boxes_appear_for_non_text_questions_only(self):
        # Instructor creates a survey with multiple question types
        self.login("instructor@test.com")

        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)

        # Create one of each question type
        text_q = Question.objects.create(
            survey=survey, text="Text question", question_type="text"
        )
        mc_q = Question.objects.create(
            survey=survey,
            text="MC question",
            question_type="multiple_choice",
            options=["A", "B"],
        )
        rating_q = Question.objects.create(
            survey=survey,
            text="Rating question",
            question_type="rating",
            options=[1, 2, 3],
        )
        checkbox_q = Question.objects.create(
            survey=survey,
            text="Checkbox question",
            question_type="checkbox",
            options=["X", "Y"],
        )
        yn_q = Question.objects.create(
            survey=survey,
            text="Yes/No question",
            question_type="yes_no",
            options=["Yes", "No"],
        )
        self.logout()

        # A student visits the survey
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        # They notice that text questions don't have comment boxes
        self.assertFalse(survey_page.comment_box_exists(text_q.id))

        # But all other question types (MC, rating, checkbox, yes/no) have optional comment boxes
        for q in [mc_q, rating_q, checkbox_q, yn_q]:
            self.assertTrue(survey_page.comment_box_exists(q.id))
