from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import os
from unittest import skipIf

from .base import FunctionalTest
from .pages.instructor_pages import (
    InstructorDashboardPage,
    InstructorSurveyCreatePage,
    InstructorSurveyDetailPage,
)


class QuestionValidationTest(FunctionalTest):
    # helper method
    def get_error_element(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".invalid-feedback")

    def get_question_input_box(self):
        return self.browser.find_element(By.NAME, "text")

    def test_cannot_add_empty_survey_questions(self):
        # User 1 logs in
        self.login("user@example.com")

        # She creates a new survey
        dashboard = InstructorDashboardPage(self)
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Test Survey")

        # Wait for the survey editor
        self.wait_for(lambda: self.browser.find_element(By.NAME, "text"))

        # She accidentally tries to submit an empty question
        self.get_question_input_box().send_keys(Keys.ENTER)

        # The home page refreshes, and there is an error message saying
        # that question names cannot be blank
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:invalid")
        )

        # She starts typing some text for the new question and the error disappears
        self.get_question_input_box().send_keys("Why capybara?")
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:valid")
        )

        # And she can submit it successfully
        self.get_question_input_box().send_keys(Keys.ENTER)

        # Wait for the question to appear in the table
        self.wait_for(
            lambda: self.assertIn(
                "Why capybara?",
                self.browser.find_element(By.ID, "id_question_table").text,
            )
        )

        # Weirdly, she now decides to submit a second blank question
        self.get_question_input_box().send_keys(Keys.ENTER)

        # She receives a similar warning on the question page
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:invalid")
        )

        # And she can correct it by filling some text in
        self.get_question_input_box().send_keys("Why not?")
        self.get_question_input_box().send_keys(Keys.ENTER)

        # Wait for second question to appear
        self.wait_for(
            lambda: self.assertIn(
                "Why not?",
                self.browser.find_element(By.ID, "id_question_table").text,
            )
        )

    def test_cannot_add_duplicate_questions(self):
        # User 1 logs in
        self.login("user@example.com")

        # She creates a new survey
        dashboard = InstructorDashboardPage(self)
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Test Survey")

        # She adds a question
        survey_detail = InstructorSurveyDetailPage(self)
        survey_detail.add_question("Is a capybara?")

        # She accidentally tries to enter a duplicate question
        self.get_question_input_box().send_keys("Is a capybara?")
        self.get_question_input_box().send_keys(Keys.ENTER)

        # She sees a helpful error message
        self.wait_for(
            lambda: self.assertEqual(
                self.get_error_element().text,
                "You've already got this question in your survey",
            )
        )

        # She corrects it by entering a different question
        self.get_question_input_box().clear()
        self.get_question_input_box().send_keys("Why capybara?")
        self.get_question_input_box().send_keys(Keys.ENTER)

        # Now she has two questions in her survey
        # Re-find the table element after the page update
        self.wait_for(
            lambda: self.assertIn(
                "Why capybara?",
                self.browser.find_element(By.ID, "id_question_table").text,
            )
        )
        # Check both questions are present by re-finding the table
        table = self.browser.find_element(By.ID, "id_question_table")
        self.assertIn("Is a capybara?", table.text)

    @skipIf(os.environ.get("CI"), "JavaScript event handling unreliable in headless CI")
    def test_error_messages_are_cleared_on_input(self):
        # User 1 logs in
        self.login("user@example.com")

        # She creates a survey and adds a question
        dashboard = InstructorDashboardPage(self)
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Test Survey")

        survey_detail = InstructorSurveyDetailPage(self)
        survey_detail.add_question("Capybara?")

        # She causes a validation error by trying to add a duplicate
        self.get_question_input_box().send_keys("Capybara?")
        self.get_question_input_box().send_keys(Keys.ENTER)
        self.wait_for(lambda: self.assertTrue(self.get_error_element().is_displayed()))

        # She starts typing in the input box to clear the error
        self.get_question_input_box().send_keys("a")

        # She is pleased to see that the error message disappears
        self.wait_for(lambda: self.assertFalse(self.get_error_element().is_displayed()))
