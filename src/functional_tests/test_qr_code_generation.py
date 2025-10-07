from selenium.webdriver.common.by import By
from .base import FunctionalTest
from surveys.models import Survey, Question
from accounts.models import User


class QRCodeGenerationTest(FunctionalTest):

    def test_instructor_can_see_qr_code_for_their_survey(self):
        # Instructor logs in
        self.login("instructor@test.com")

        # They create a survey
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        Question.objects.create(survey=survey, text="How was the session?")

        # They visit their survey page
        self.browser.get(f"{self.live_server_url}/surveys/{survey.id}/")

        # They see a QR code image displayed
        qr_code_img = self.browser.find_element(By.CSS_SELECTOR, "img.qr-code")
        self.assertIsNotNone(qr_code_img.get_attribute("src"))

    def test_qr_code_links_to_correct_survey_url(self):
        # Instructor creates a survey
        self.login("instructor@test.com")
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        Question.objects.create(survey=survey, text="Test question")

        # They visit their survey page
        self.browser.get(f"{self.live_server_url}/surveys/{survey.id}/")

        # They see the QR code
        qr_code_img = self.browser.find_element(By.CSS_SELECTOR, "img.qr-code")
        qr_code_url = qr_code_img.get_attribute("src")

        # The QR code image is being served
        self.assertIn(f"/surveys/{survey.id}/qr/", qr_code_url)

        # When a student visits the survey URL (what the QR code encodes)
        self.browser.get(f"{self.live_server_url}/survey/{survey.id}/")

        # They see the survey question
        self.assertIn("Test question", self.browser.page_source)
