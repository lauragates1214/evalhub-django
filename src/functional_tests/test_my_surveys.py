from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest
from .survey_page import SurveyPage


class MySurveysTest(FunctionalTest):
    def test_logged_in_users_surveys_are_saved(self):
        # A logged-in user visits the site
        email = "user@example.com"
        self.login(email)

        # They go to home page and create a survey
        self.browser.get(self.live_server_url)

        # They enter a name for their survey
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Capybara Feedback")

        # Then add their first question
        inputbox = self.browser.find_element(By.ID, "id_text")
        inputbox.send_keys("What's your least favourite capybara?")
        inputbox.send_keys(Keys.ENTER)

        # They can add more questions
        survey_page = SurveyPage(self)
        survey_page.wait_for_row_in_question_table(
            "What's your least favourite capybara?", 1
        )
        survey_page.add_survey_question("Why and how?")
        first_survey_url = self.browser.current_url

        # They notice a "My Surveys" link
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()

        # They see their survey listed by the name they chose
        self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, "Capybara Feedback")
        )
        self.browser.find_element(By.LINK_TEXT, "Capybara Feedback").click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_survey_url)
        )

        # They decide to start another survey
        self.browser.get(self.live_server_url)
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Cow Survey")
        inputbox = self.browser.find_element(By.ID, "id_text")
        inputbox.send_keys("Click cows?")
        inputbox.send_keys(Keys.ENTER)

        survey_page = SurveyPage(self)
        survey_page.wait_for_row_in_question_table("Click cows?", 1)
        second_survey_url = self.browser.current_url

        # Under "my surveys", both surveys appear with their chosen names
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()
        self.wait_for(lambda: self.browser.find_element(By.LINK_TEXT, "Cow Survey"))
        self.browser.find_element(By.LINK_TEXT, "Cow Survey").click()
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

    def test_cannot_create_survey_without_name(self):
        # User logs in
        self.login("user@example.com")

        # She goes to the home page and tries to create a survey without entering a name
        self.browser.get(self.live_server_url)

        # She enters a question but no survey name
        inputbox = self.browser.find_element(By.ID, "id_text")
        inputbox.send_keys("First question")
        inputbox.send_keys(Keys.ENTER)

        # The browser prevents submission with HTML5 validation
        self.wait_for(
            lambda: self.browser.find_element(
                By.CSS_SELECTOR, "#id_survey_name:invalid"
            )
        )

        # She enters a survey name
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("My Survey")

        # Now the survey name field is valid
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_survey_name:valid")
        )

        # She can now successfully submit
        inputbox.send_keys(Keys.ENTER)

        # She's redirected to the survey page with her question
        survey_page = SurveyPage(self)
        survey_page.wait_for_row_in_question_table("First question", 1)
