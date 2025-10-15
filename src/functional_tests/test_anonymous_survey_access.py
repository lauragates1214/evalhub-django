from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from .base import FunctionalTest
from .pages import StudentSurveyPage


class AnonymousSurveyAccessTest(FunctionalTest):
    def test_student_can_access_survey_via_qr_code_link(self):
        # Instructor logs in, creates a survey with questions, then logs out
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions(
            "instructor@test.com", ["How was the session?", "Any suggestions?"]
        )
        self.logout()

        # Student scans QR code (simulated by visiting the survey URL directly)
        # QR code would encode something like: /survey/abc123/
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        # They see the survey title and first question
        survey_page.check_question_exists("How was the session?")

        # They fill in their response to the first question
        survey_page.fill_text_response_by_number(1, "It was great!")

        # They see and fill in the second question
        survey_page.check_question_exists("Any suggestions?")
        survey_page.fill_text_response_by_number(2, "More examples please")

        # They submit the survey
        survey_page.submit()

        # They see a confirmation message
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "confirmation-message"))
        )
        confirmation = self.browser.find_element(By.CLASS_NAME, "confirmation-message")
        self.assertIn("Thank you", confirmation.text)
