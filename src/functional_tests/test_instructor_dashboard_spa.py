# src/functional_tests/test_instructor_dashboard_spa.py

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest
from accounts.models import User
from surveys.models import Survey


class InstructorDashboardSPATest(FunctionalTest):
    def test_instructor_experiences_spa_like_navigation(self):
        # Sarah is an instructor who logs into EvalHub
        self.login("sarah@instructor.com")

        # After logging in, she's taken to her dashboard
        # which has a persistent navigation sidebar and main content area
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.current_url, self.live_server_url + "/dashboard/"
            )
        )

        # She sees a navigation sidebar that won't disappear during navigation
        sidebar = self.browser.find_element(By.ID, "dashboard-sidebar")
        self.assertIn("My Surveys", sidebar.text)
        self.assertIn("Create Survey", sidebar.text)
        self.assertIn("Analytics", sidebar.text)

        # The main content area shows her survey list by default
        main_content = self.browser.find_element(By.ID, "main-content")
        self.assertIn("Your Surveys", main_content.text)

        # She clicks "Create Survey" in the sidebar
        create_link = sidebar.find_element(By.LINK_TEXT, "Create Survey")
        create_link.click()

        # The page doesn't reload - only the main content area changes
        # The sidebar is still there unchanged
        self.wait_for(
            lambda: self.assertIn(
                "Create New Survey",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # Verify the sidebar is still present and unchanged
        sidebar = self.browser.find_element(By.ID, "dashboard-sidebar")
        self.assertIn("My Surveys", sidebar.text)

        # The URL has changed to reflect the new view
        self.assertEqual(
            self.browser.current_url, self.live_server_url + "/dashboard/surveys/new/"
        )

        # She creates a survey with a name
        survey_name_input = self.browser.find_element(By.NAME, "survey_name")
        survey_name_input.send_keys("Mid-term Feedback")
        survey_name_input.send_keys(Keys.ENTER)

        # After creating, the main content updates to show the survey editor
        # Still no full page reload - sidebar remains
        self.wait_for(
            lambda: self.assertIn(
                "Mid-term Feedback",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # She clicks "My Surveys" to go back to the list
        my_surveys_link = sidebar.find_element(By.LINK_TEXT, "My Surveys")
        my_surveys_link.click()

        # Again, only the content area updates - showing her new survey in the list
        self.wait_for(
            lambda: self.assertIn(
                "Mid-term Feedback",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # The sidebar never flickered or reloaded throughout the entire experience
        sidebar = self.browser.find_element(By.ID, "dashboard-sidebar")
        self.assertIn("Create Survey", sidebar.text)
