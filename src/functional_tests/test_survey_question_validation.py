from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class ItemValidationTest(FunctionalTest):
    def test_cannot_add_empty_survey_questions(self):
        # User 1 goes to the home page and accidentally tries to submit
        # an empty question. She hits Enter on the empty input box
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.ID, "id_new_question").send_keys(Keys.ENTER)

        # The home page refreshes, and there is an error message saying
        # that question names cannot be blank
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_element(By.CSS_SELECTOR, ".invalid-feedback").text,
                "You can't have an empty question",
            )
        )

        # She tries again with some text for the question, which now works
        self.browser.find_element(By.ID, "id_new_question").send_keys("Why capybara?")
        self.browser.find_element(By.ID, "id_new_question").send_keys(Keys.ENTER)
        self.wait_for_row_in_survey_table("1: Why capybara?")

        return  # TODO reenable the rest of this test

        # Perversely, she now descides to submit a second blank question
        self.browser.find_element(By.ID, "id_new_question").send_keys(Keys.ENTER)

        # She receives a similar warning on the question page
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_element(By.CSS_SELECTOR, ".invalid-feedback").text,
                "You can't have an empty question",
            )
        )

        # And she can correct it by filling some text in
        self.browser.find_element(By.ID, "id_new_question").send_keys("Why not?")
        self.browser.find_element(By.ID, "id_new_question").send_keys(Keys.ENTER)
        self.wait_for_row_in_survey_table("2: Why not?")
