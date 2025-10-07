from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest
from .survey_page import SurveyPage


class NewVisitorTest(FunctionalTest):
    # Acts as regression test
    def test_can_start_a_new_question(self):
        # User 1 logs in
        self.login("user@example.com")

        # She goes to the EvalHub homepage to register as a new user
        self.browser.get(self.live_server_url)

        # She notices the page title mentions EvalHub
        self.assertIn("EvalHub", self.browser.title)

        # She notices the header mentions surveys
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Survey", header_text)

        # She is invited to create a new question
        survey_page = SurveyPage(self)
        inputbox = survey_page.get_question_input_box()

        self.assertEqual(
            inputbox.get_attribute("placeholder"), "Enter a survey question"
        )

        # She types her first question and hits enter
        survey_page.add_survey_question("How do you feel about capybara?")

        # There is still a text box inviting her to add another question.
        # She enters another question and hits enter
        survey_page.add_survey_question("How many capybara? Explain.")

        # The page updates again, and now shows both questions in her list
        survey_page.wait_for_row_in_question_table("How do you feel about capybara?", 1)
        survey_page.wait_for_row_in_question_table("How many capybara? Explain.", 2)

        # Satisfied, she logs out to continue later.

    def test_multiple_users_can_start_questions_at_different_urls(self):
        # User 1 logs in
        self.login("user1@example.com")

        # She starts a new survey
        survey_page = SurveyPage(self).go_to_new_survey_page()
        survey_page.add_survey_question("How do you feel about capybara?")

        # She notices that her survey has a unique URL
        user1_survey_url = self.browser.current_url
        self.assertRegex(user1_survey_url, "/surveys/.+")

        # Now a new user, User 2, comes along to the site
        ## Delete all the browser's cookies as a way of simulating a brand new user session
        self.browser.delete_all_cookies()

        # User 2 logs in
        self.login("user2@example.com")

        # User 2 visits the home page. There is no sign of User 1's question
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("How do you feel about capybara?", page_text)

        # User 2 starts a new survey by entering a new question
        survey_page = SurveyPage(self)
        survey_page.add_survey_question("Why manatee? Explain.")

        # User 2 gets their own unique URL
        user2_survey_url = self.browser.current_url
        self.assertRegex(user2_survey_url, "/surveys/.+")
        self.assertNotEqual(user2_survey_url, user1_survey_url)

        # Again, there is no trace of User 1's question
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("How do you feel about capybara?", page_text)
        self.assertIn("Why manatee? Explain.", page_text)

        # Satisfied, they both go back to sleep

    def test_instructor_can_name_their_survey(self):
        # Instructor logs in
        self.login("instructor@test.com")

        # She goes to create a new survey
        self.browser.get(self.live_server_url)

        # Before she adds any questions, she sees a field to name her survey
        name_input = self.browser.find_element(By.NAME, "survey_name")
        self.assertEqual(
            name_input.get_attribute("placeholder"), "Enter a name for your survey"
        )

        # She enters a name for her survey
        name_input.send_keys("Q4 Capybara Evaluation")

        # She adds her first question by typing and hitting enter
        inputbox = self.browser.find_element(By.ID, "id_text")
        inputbox.send_keys("How did you find the capybara?")
        inputbox.send_keys(Keys.ENTER)

        # Wait to be redirected to the survey page
        from .survey_page import SurveyPage

        survey_page = SurveyPage(self)
        survey_page.wait_for_row_in_question_table("How did you find the capybara?", 1)

        # She goes to "My Surveys"
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()

        # She sees her survey listed by the name she chose, not by the first question
        self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, "Q4 Capybara Evaluation")
        )
        self.assertNotIn("How did you find the capybara?", self.browser.page_source)
