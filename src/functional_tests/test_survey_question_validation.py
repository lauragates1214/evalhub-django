from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from unittest import skip

from .base import FunctionalTest


class QuestionValidationTest(FunctionalTest):
    # helper method
    def get_error_element(self):
        return self.browser.find_element(By.CSS_SELECTOR, ".invalid-feedback")

    def test_cannot_add_empty_survey_questions(self):
        # User 1 logs in
        self.login("user@example.com")

        # She goes to the home page and accidentally tries to submit
        # an empty question. She hits Enter on the empty input box
        self.browser.get(self.live_server_url)
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
        self.wait_for_row_in_survey_table("1: Why capybara?")

        # Weirdly, she now descides to submit a second blank question
        self.get_question_input_box().send_keys(Keys.ENTER)

        # She receives a similar warning on the question page
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:invalid")
        )

        # And she can correct it by filling some text in
        self.get_question_input_box().send_keys("Why not?")
        self.get_question_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_survey_table("2: Why not?")

    def test_cannot_add_duplicate_questions(self):
        # User 1 logs in
        self.login("user@example.com")

        # She goes to the home page and starts a new survey
        self.browser.get(self.live_server_url)
        self.get_question_input_box().send_keys("Is a capybara?")
        self.get_question_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_survey_table("1: Is a capybara?")

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
        self.wait_for_row_in_survey_table("1: Is a capybara?")
        self.wait_for_row_in_survey_table("2: Why capybara?")

    def test_error_messages_are_cleared_on_input(self):
        # User 1 logs in
        self.login("user@example.com")

        # She starts a survey and causes a validation error:
        self.browser.get(self.live_server_url)
        self.get_question_input_box().send_keys("Capybara?")
        self.get_question_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_survey_table("1: Capybara?")
        self.get_question_input_box().send_keys("Capybara?")
        self.get_question_input_box().send_keys(Keys.ENTER)
        self.wait_for(lambda: self.assertTrue(self.get_error_element().is_displayed()))

        # She starts typing in the input box to clear the error
        self.get_question_input_box().send_keys("a")

        # She is pleased to see that the error message disappears
        self.wait_for(lambda: self.assertFalse(self.get_error_element().is_displayed()))
