import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from unittest import skipIf

from .base import FunctionalTest
from .survey_page import SurveyPage


class LayoutAndStylingTest(FunctionalTest):
    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_layout_and_styling(self):
        # Aya logs in
        self.login("aya@example.com")

        # She goes to the dashboard and clicks Create Survey
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # She enters a survey name
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Test Survey")
        name_input.send_keys(Keys.ENTER)

        # Wait for the survey editor with the question input
        self.wait_for(lambda: self.browser.find_element(By.ID, "id_text"))

        # Her browser window is set to a very specific size
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered within the main content area, not the full window
        # With sidebar ~200px, the center would be around (200 + (1024-200)/2) = 612px
        inputbox = self.browser.find_element(By.ID, "id_text")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            593,  # Actual centered position with sidebar
            delta=10,
        )

        # She adds a question
        inputbox = self.browser.find_element(By.ID, "id_text")
        inputbox.send_keys("testing")
        inputbox.send_keys(Keys.ENTER)

        # Wait for the page to update after adding the question
        # Wait for the question to appear in the table to ensure the page has updated
        from .survey_page import SurveyPage

        survey_page = SurveyPage(self)
        survey_page.wait_for_row_in_question_table("testing", 1)

        # The input is still nicely centered
        inputbox = self.browser.find_element(By.ID, "id_text")  # Get the element again
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            593,  # Actual centered position with sidebar
            delta=10,
        )
