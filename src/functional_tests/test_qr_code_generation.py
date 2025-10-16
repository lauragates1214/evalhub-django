from selenium.webdriver.common.by import By
from .base import FunctionalTest
from .pages.instructor_pages import InstructorSurveyDetailPage


class QRCodeGenerationTest(FunctionalTest):
    def test_instructor_can_see_qr_code_for_their_survey(self):
        # Instructor logs in and creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions(
            "instructor@test.com", ["Test question"]
        )

        # They visit their survey page
        survey_detail = InstructorSurveyDetailPage(self)
        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # They see a QR code displayed
        survey_detail.check_qr_code_visible()

    def test_qr_code_links_to_correct_survey_url(self):
        # Instructor creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions(
            "instructor@test.com", ["Test question"]
        )

        # They visit their survey page
        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # They see the QR code
        qr_code_img = self.browser.find_element(By.CSS_SELECTOR, "img.qr-code")
        qr_code_url = qr_code_img.get_attribute("src")

        # The QR code image is being served
        self.assertIn(f"instructor/survey/{survey.id}/qr/", qr_code_url)

        # When a student visits the survey URL (what the QR code encodes)
        self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

        # They see the survey question
        self.assertIn("Test question", self.browser.page_source)
