from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import FunctionalTest
from surveys.models import Survey, Question
from accounts.models import User


class AnonymousSurveyAccessTest(FunctionalTest):
    def test_student_can_access_survey_via_qr_code_link(self):
        # Instructor creates a survey with questions
        instructor = User.objects.create_user(
            email="instructor@test.com", password="password"
        )
        survey = Survey.objects.create(owner=instructor)
        Question.objects.create(survey=survey, text="How was the session?")
        Question.objects.create(survey=survey, text="Any suggestions?")

        # Student scans QR code (simulated by visiting the survey URL directly)
        # QR code would encode something like: /survey/abc123/
        survey_url = f"{self.live_server_url}/survey/{survey.id}/"
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
