from django.urls import reverse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base import FunctionalTest


class AnonymousSurveyAccessTest(FunctionalTest):
    def test_student_can_access_survey_via_qr_code_link(self):
        # Instructor creates a survey with questions
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions(
            "instructor@test.com", ["How was the session?", "Any suggestions?"]
        )

        # Student scans QR code (simulated by visiting the survey URL directly)
        # QR code would encode something like: /survey/abc123/
        survey_url = self.live_server_url + reverse(
            "students:take_survey", args=[survey.id]
        )
        self.browser.get(survey_url)

        # They see the survey title and first question
        self.assertIn("How was the session?", self.browser.page_source)

        # They fill in their response to the first question
        response_input = self.browser.find_element(By.NAME, "response_1")
        response_input.send_keys("It was great!")

        # They see and fill in the second question
        self.assertIn("Any suggestions?", self.browser.page_source)
        response_input_2 = self.browser.find_element(By.NAME, "response_2")
        response_input_2.send_keys("More examples please")

        # They submit the survey
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        submit_button.click()

        # They see a confirmation message
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "confirmation-message"))
        )
        confirmation = self.browser.find_element(By.CLASS_NAME, "confirmation-message")
        self.assertIn("Thank you", confirmation.text)
