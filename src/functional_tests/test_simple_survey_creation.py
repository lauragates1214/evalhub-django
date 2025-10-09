from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest
from .survey_page import SurveyPage


class NewVisitorTest(FunctionalTest):
    # Acts as regression test
    def test_can_start_a_new_question(self):
        # Emma is an instructor who wants to create a survey
        # She logs into EvalHub
        self.login("user@example.com")

        # After logging in, she's taken to her dashboard
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.current_url, self.live_server_url + "/dashboard/"
            )
        )

        # She sees the page title mentions Dashboard
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Dashboard", header_text)

        # She notices a "Create Survey" option in the sidebar and clicks it
        sidebar = self.browser.find_element(By.ID, "dashboard-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # The main area updates to show a survey creation form
        self.wait_for(
            lambda: self.assertIn(
                "Create New Survey",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # She enters a name for her survey
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Test Survey")
        name_input.send_keys(Keys.ENTER)

        # The survey is created and she sees a form to add questions
        self.wait_for(lambda: self.browser.find_element(By.NAME, "text"))

        # She adds her first question about capybaras
        survey_page = SurveyPage(self)
        survey_page.add_survey_question("How do you feel about capybara?")

        # The page updates and shows her question in a list
        survey_page.wait_for_row_in_question_table("How do you feel about capybara?", 1)

        # She adds another question
        survey_page.add_survey_question("How many capybara? Explain.")

        # Now she sees both questions listed
        survey_page.wait_for_row_in_question_table("How many capybara? Explain.", 2)

        # Satisfied, she logs out
        self.browser.find_element(By.CSS_SELECTOR, "#id_logout").click()

    def test_multiple_users_can_start_questions_at_different_urls(self):
        # Zhi logs in and creates a survey
        self.login("user1@example.com")

        # He's on the dashboard and clicks Create Survey
        sidebar = self.browser.find_element(By.ID, "dashboard-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # He creates a survey
        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Zhi's Survey")
        name_input.send_keys(Keys.ENTER)

        # He adds a question
        self.wait_for(lambda: self.browser.find_element(By.ID, "id_text"))
        survey_page = SurveyPage(self)
        survey_page.add_survey_question("How do you feel about capybara?")

        # He notices that his survey has a unique URL
        user1_survey_url = self.browser.current_url
        self.assertRegex(user1_survey_url, "/surveys/.+")

        # Now a new user, Kerrie, comes along to the site
        # We use a new browser session to simulate a new user
        self.browser.delete_all_cookies()

        # Kerrie logs in
        self.login("user2@example.com")

        # Kerrie is on her dashboard
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.current_url, self.live_server_url + "/dashboard/"
            )
        )

        # Kerrie creates her own survey
        sidebar = self.browser.find_element(By.ID, "dashboard-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Kerrie's Survey")
        name_input.send_keys(Keys.ENTER)

        # She adds a different question
        self.wait_for(lambda: self.browser.find_element(By.ID, "id_text"))
        survey_page = SurveyPage(self)
        survey_page.add_survey_question("Why manatee? Explain.")

        # Kerrie gets her own unique URL
        user2_survey_url = self.browser.current_url
        self.assertRegex(user2_survey_url, "/surveys/.+")
        self.assertNotEqual(user2_survey_url, user1_survey_url)

        # There is no trace of Zhi's survey question
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("How do you feel about capybara?", page_text)
        self.assertIn("Why manatee? Explain.", page_text)

        # Satisfied, they both go back to sleep

    def test_instructor_can_name_their_survey(self):
        # Instructor logs in
        self.login("instructor@test.com")  # This redirects to dashboard

        # She clicks "Create Survey" in the sidebar
        sidebar = self.browser.find_element(By.ID, "dashboard-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # She sees a field to name her survey
        name_input = self.browser.find_element(By.NAME, "survey_name")
        self.assertEqual(
            name_input.get_attribute("placeholder"),
            "Survey name",  # Note: might need to check what the actual placeholder is
        )

        # She enters a name for her survey
        name_input.send_keys("Q4 Capybara Evaluation")
        name_input.send_keys(Keys.ENTER)

        # Wait for the survey to be created and editor to load
        self.wait_for(
            lambda: self.assertIn(
                "Q4 Capybara Evaluation",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # She adds her first question
        inputbox = self.browser.find_element(By.NAME, "text")
        inputbox.send_keys("How did you find the capybara?")
        inputbox.send_keys(Keys.ENTER)

        # She goes to "My Surveys" via the sidebar
        sidebar = self.browser.find_element(
            By.ID, "dashboard-sidebar"
        )  # Re-find sidebar
        sidebar.find_element(By.LINK_TEXT, "My Surveys").click()

        # She sees her survey listed by name in the main content
        main_content = self.browser.find_element(By.ID, "main-content")
        self.wait_for(
            lambda: self.assertIn("Q4 Capybara Evaluation", main_content.text)
        )
        self.assertNotIn("How did you find the capybara?", main_content.text)
