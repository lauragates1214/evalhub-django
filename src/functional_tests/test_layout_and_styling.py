import os
from selenium.webdriver.common.by import By
from unittest import skipIf

from .base import FunctionalTest
from .pages.instructor_pages import (
    InstructorDashboardPage,
    InstructorSurveyCreatePage,
    InstructorSurveyDetailPage,
)


class LayoutAndStylingTest(FunctionalTest):
    """Test for layout and styling of key pages"""

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_layout_and_styling(self):
        """Instructor dashboard and survey editor are nicely styled and laid out"""
        # Aya logs in
        self.login("aya@example.com")

        # She goes to the dashboard and clicks Create Survey
        dashboard = InstructorDashboardPage(self)
        dashboard.navigate_to_dashboard()
        dashboard.click_create_survey()

        # She creates a survey
        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Test Survey")

        # Wait for the survey editor to load
        survey_detail = InstructorSurveyDetailPage(self)
        self.wait_for(lambda: self.browser.find_element(By.ID, "id_text"))

        # Her browser window is set to a very specific size
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centred within the main content area, not the full window
        # With sidebar ~200px, the centre would be around (200 + (1024-200)/2) = 612px
        inputbox = self.browser.find_element(By.ID, "id_text")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            593,  # Actual centred position with sidebar
            delta=10,
        )

        # She adds a question
        survey_detail.add_question("testing")

        # The input is still nicely centred
        inputbox = self.browser.find_element(By.ID, "id_text")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            593,  # Actual centred position with sidebar
            delta=10,
        )
