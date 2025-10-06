from selenium.webdriver.common.by import By

from .base import FunctionalTest
from .survey_page import SurveyPage


class MySurveysTest(FunctionalTest):
    def test_logged_in_users_surveys_are_saved(self):
        email = "user@example.com"

        # User1 logs in
        self.login(email)

        # They go to home page and create a survey
        survey_page = SurveyPage(self).go_to_new_survey_page()
        survey_page.add_survey_question("What's your least favourite capybara?")
        survey_page.add_survey_question("Why and how?")
        first_survey_url = self.browser.current_url

        # They notice a "My Surveys" link
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()

        # They see their email in the page heading
        self.wait_for(
            lambda: self.assertIn(
                email,
                self.browser.find_element(By.CSS_SELECTOR, "h1").text,
            )
        )

        # They see their survey listed, named after its first question
        self.wait_for(
            lambda: self.browser.find_element(
                By.LINK_TEXT, "What's your least favourite capybara?"
            )
        )
        self.browser.find_element(
            By.LINK_TEXT, "What's your least favourite capybara?"
        ).click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_survey_url)
        )

        # They decide to start another survey, just to see
        survey_page = SurveyPage(self).go_to_new_survey_page()
        survey_page.add_survey_question("Click cows?")
        second_survey_url = self.browser.current_url

        # Under "my surveys", their new survey appears
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()
        self.wait_for(lambda: self.browser.find_element(By.LINK_TEXT, "Click cows?"))
        self.browser.find_element(By.LINK_TEXT, "Click cows?").click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_survey_url)
        )

        # They log out. The "My Surveys" option disappears
        self.browser.find_element(By.CSS_SELECTOR, "#id_logout").click()
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_elements(By.LINK_TEXT, "My Surveys"),
                [],
            )
        )
