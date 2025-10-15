from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest
from .survey_page import SurveyPage


class MySurveysTest(FunctionalTest):
    def test_logged_in_users_surveys_are_saved(self):
        # A logged-in user visits the site
        email = "user@example.com"
        self.login(email)  # This redirects to /dashboard/

        # They're now on the dashboard - they click "Create Survey"
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # They enter a name for their survey
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Capybara Feedback")
        name_input.send_keys(Keys.ENTER)

        # Wait for the survey editor to load after creation
        self.wait_for(lambda: self.browser.find_element(By.NAME, "text"))

        # The survey is created and they see the survey editor
        # They add their first question
        inputbox = self.browser.find_element(By.NAME, "text")
        inputbox.send_keys("What's your least favourite capybara?")
        inputbox.send_keys(Keys.ENTER)

        # After adding questions, they navigate back to My Surveys
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "My Surveys").click()

        # They see their survey listed by the name they chose
        self.wait_for(
            lambda: self.assertIn(
                "Capybara Feedback",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # After seeing the first survey in My Surveys, create another survey
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # Wait for the create form to load
        self.wait_for(lambda: self.browser.find_element(By.NAME, "survey_name"))

        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Cow Survey")
        name_input.send_keys(Keys.ENTER)

        # Now wait for the survey editor with the text input
        self.wait_for(lambda: self.browser.find_element(By.NAME, "text"))

        inputbox = self.browser.find_element(By.NAME, "text")
        inputbox.send_keys("Click cows?")
        inputbox.send_keys(Keys.ENTER)

        # Navigate back to My Surveys
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "My Surveys").click()

        # Both surveys should be listed
        main_content = self.browser.find_element(By.ID, "main-content")
        self.wait_for(lambda: self.assertIn("Capybara Feedback", main_content.text))
        self.assertIn("Cow Survey", main_content.text)

        # They log out. The dashboard is no longer accessible
        self.browser.find_element(By.CSS_SELECTOR, "#id_logout").click()
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_elements(By.ID, "instructor-sidebar"),
                [],
            )
        )

    def test_cannot_create_survey_without_name(self):
        # Jaydean logs in
        self.login("jaydean@example.com")

        # She goes to create a survey
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # She tries to submit without entering a name
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys(Keys.ENTER)

        # The browser prevents submission with HTML5 validation
        self.wait_for(
            lambda: self.browser.find_element(
                By.CSS_SELECTOR, '[name="survey_name"]:invalid'
            )
        )

        # She enters a survey name
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("My Survey")

        # Now the survey name field is valid
        self.wait_for(
            lambda: self.browser.find_element(
                By.CSS_SELECTOR, '[name="survey_name"]:valid'
            )
        )

        # She can now successfully submit
        name_input.send_keys(Keys.ENTER)

        # She's taken to the survey editor
        self.wait_for(lambda: self.browser.find_element(By.ID, "id_text"))
