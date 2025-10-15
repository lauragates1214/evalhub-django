from selenium.webdriver.common.by import By
from .base import FunctionalTest
from surveys.models import Survey, Question
from accounts.models import User


class MultipleChoiceQuestionTest(FunctionalTest):
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
        self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

        # They see radio buttons for the multiple choice question
        self.assertIn("How would you rate this course?", self.browser.page_source)
        excellent_radio = self.browser.find_element(
            By.CSS_SELECTOR, 'input[type="radio"][value="Excellent"]'
        )

        # They select an option
        excellent_radio.click()

        # They can also add an optional comment
        comment_box = self.browser.find_element(By.NAME, f"comment_{question.id}")
        comment_box.send_keys("Great instructor!")

        # They submit
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        submit_button.click()

        # They see confirmation
        self.wait_for(lambda: self.assertIn("Thank you", self.browser.page_source))


class RatingScaleQuestionTest(FunctionalTest):
    def test_student_can_answer_rating_scale_question(self):
        # Instructor creates a survey with a rating scale question
        # Create and login the instructor
        self.login("instructor@test.com")

        # Get the user and create the survey with custom question
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        question = Question.objects.create(
            survey=survey,
            text="How likely are you to recommend capybara?",
            question_type="rating",
            options=[1, 2, 3, 4, 5],  # 1-5 scale
        )
        self.logout()

        # Student visits the survey
        self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

        # They see radio buttons for the rating scale
        self.assertIn(
            "How likely are you to recommend capybara?", self.browser.page_source
        )
        rating_5 = self.browser.find_element(
            By.CSS_SELECTOR, 'input[type="radio"][value="5"]'
        )

        # They select a rating
        rating_5.click()

        # They can add an optional comment
        comment_box = self.browser.find_element(By.NAME, f"comment_{question.id}")
        comment_box.send_keys("Best capybara ever!")

        # They submit
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        submit_button.click()

        # They see confirmation
        self.wait_for(lambda: self.assertIn("Thank you", self.browser.page_source))


class CheckboxQuestionTest(FunctionalTest):
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
        self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

        # They see checkboxes
        self.assertIn("Which topics interested you most?", self.browser.page_source)
        python_checkbox = self.browser.find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"][value="Capybara"]'
        )
        testing_checkbox = self.browser.find_element(
            By.CSS_SELECTOR, 'input[type="checkbox"][value="Capybaras"]'
        )

        # They select multiple options
        python_checkbox.click()
        testing_checkbox.click()

        # They can add a comment
        comment_box = self.browser.find_element(By.NAME, f"comment_{question.id}")
        comment_box.send_keys("Looking forward to more cap!")

        # They submit
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        submit_button.click()

        # They see confirmation
        self.wait_for(lambda: self.assertIn("Thank you", self.browser.page_source))


class YesNoQuestionTest(FunctionalTest):
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
        self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

        # They see radio buttons for yes/no
        self.assertIn("Would you capybara?", self.browser.page_source)
        yes_radio = self.browser.find_element(
            By.CSS_SELECTOR, 'input[type="radio"][value="Yes"]'
        )

        # They select an option
        yes_radio.click()

        # They can add a comment
        comment_box = self.browser.find_element(By.NAME, f"comment_{question.id}")
        comment_box.send_keys("Definitely!")

        # They submit
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        submit_button.click()

        # They see confirmation
        self.wait_for(lambda: self.assertIn("Thank you", self.browser.page_source))


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
    self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

    # They notice that text questions don't have comment boxes
    from selenium.common.exceptions import NoSuchElementException

    with self.assertRaises(NoSuchElementException):
        self.browser.find_element(By.NAME, f"comment_{text_q.id}")

    # But all other question types (MC, rating, checkbox, yes/no) have optional comment boxes
    for q in [mc_q, rating_q, checkbox_q, yn_q]:
        comment_box = self.browser.find_element(By.NAME, f"comment_{q.id}")
        self.assertIsNotNone(comment_box)
