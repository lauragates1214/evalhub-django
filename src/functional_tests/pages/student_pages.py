from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class StudentSurveyPage:
    """Page object for student survey taking pages"""

    def __init__(self, test):
        self.test = test

    def navigate_to_survey(self, survey_id):
        """Navigate to a survey page"""
        self.test.browser.get(
            f"{self.test.live_server_url}/student/survey/{survey_id}/"
        )
        return self

    def check_question_exists(self, question_text):
        """Verify a question appears on the page"""
        self.test.assertIn(question_text, self.test.browser.page_source)
        return self

    def select_radio_option(self, value):
        """Select a radio button by value (for multiple choice, yes/no, rating)"""
        radio = self.test.browser.find_element(
            By.CSS_SELECTOR, f'input[type="radio"][value="{value}"]'
        )
        radio.click()
        return self

    def select_checkbox_option(self, value):
        """Select a checkbox by value"""
        checkbox = self.test.browser.find_element(
            By.CSS_SELECTOR, f'input[type="checkbox"][value="{value}"]'
        )
        checkbox.click()
        return self

    def fill_text_input(self, input_name, text):
        """Fill in a text input by name attribute"""
        text_input = self.test.browser.find_element(By.NAME, input_name)
        text_input.send_keys(text)
        return self

    def fill_text_response_by_number(self, question_number, text):
        """Fill in a text response using response_N naming pattern"""
        return self.fill_text_input(f"response_{question_number}", text)

    def fill_text_response_by_id(self, question_id, text):
        """Fill in a text response using response_{question.id} naming pattern"""
        return self.fill_text_input(f"response_{question_id}", text)

    def add_comment(self, question_id, comment_text):
        """Add a comment for a question"""
        comment_box = self.test.browser.find_element(By.NAME, f"comment_{question_id}")
        comment_box.send_keys(comment_text)
        return self

    def comment_box_exists(self, question_id):
        """Check if a comment box exists for a question"""
        try:
            self.test.browser.find_element(By.NAME, f"comment_{question_id}")
            return True
        except NoSuchElementException:
            return False

    def submit(self):
        """Submit the survey form"""
        submit_button = self.test.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        submit_button.click()
        return self

    def wait_for_confirmation(self):
        """Wait for and verify the thank you confirmation message"""
        self.test.wait_for(
            lambda: self.test.assertIn("Thank you", self.test.browser.page_source)
        )
        return self
