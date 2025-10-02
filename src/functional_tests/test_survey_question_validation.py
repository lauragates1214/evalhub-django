from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class QuestionValidationTest(FunctionalTest):
    def test_cannot_add_empty_survey_questions(self):
        # User 1 goes to the home page and accidentally tries to submit
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

        # Perversely, she now descides to submit a second blank question
        self.get_question_input_box().send_keys(Keys.ENTER)

        # She receives a similar warning on the question page
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:invalid")
        )

        # And she can correct it by filling some text in
        self.get_question_input_box().send_keys("Why not?")
        self.get_question_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_survey_table("2: Why not?")
