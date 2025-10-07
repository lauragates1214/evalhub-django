from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import wait


class SurveyPage:
    def __init__(self, test):
        self.test = test  # Initialized with an object that represents the current test

    def get_table_rows(self):
        return self.test.browser.find_elements(By.CSS_SELECTOR, "#id_question_table tr")

    @wait
    def wait_for_row_in_question_table(self, question_text, question_number):
        expected_row_text = f"{question_number}: {question_text}"
        rows = self.get_table_rows()
        self.test.assertIn(expected_row_text, [row.text for row in rows])

    def get_question_input_box(self):
        return self.test.browser.find_element(By.ID, "id_text")

    def add_survey_question(self, question_text, survey_name="Test Survey"):
        # Check if on the home page (creating new survey)
        survey_name_inputs = self.test.browser.find_elements(By.ID, "id_survey_name")
        if survey_name_inputs:
            # Fill in the survey name
            survey_name_inputs[0].send_keys(survey_name)

        new_question_no = len(self.get_table_rows()) + 1
        self.get_question_input_box().send_keys(question_text)
        self.get_question_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_question_table(question_text, new_question_no)
        return self  # Return the instance for method chaining

    def go_to_new_survey_page(self):
        self.test.browser.get(self.test.live_server_url)
        return self
