from selenium.webdriver.common.by import By

from .base import FunctionalTest
from .pages.instructor_pages import (
    InstructorDashboardPage,
    InstructorSurveyCreatePage,
    InstructorSurveyDetailPage,
)


class NewVisitorTest(FunctionalTest):
    """A new visitor to the site can create a survey and add questions"""

    # Acts as regression test
    def test_can_start_a_new_question(self):
        """Instructor can create a survey and add questions to it"""

        # Emma is an instructor who wants to create a survey
        # She logs into EvalHub
        self.login("user@example.com")

        # After logging in, she's taken to her dashboard
        dashboard = InstructorDashboardPage(self)
        dashboard.wait_for_url("/instructor/")

        # She sees the page title mentions Dashboard
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Dashboard", header_text)

        # She notices a "Create Survey" option in the sidebar and clicks it
        dashboard.click_create_survey()

        # The main area updates to show a survey creation form
        dashboard.wait_for_content("Create New Survey")

        # She creates her survey
        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Test Survey")

        # The survey is created and she sees a form to add questions
        survey_detail = InstructorSurveyDetailPage(self)
        self.wait_for(lambda: self.browser.find_element(By.NAME, "text"))

        # She adds her first question about capybaras
        survey_detail.add_question("How do you feel about capybara?")

        # She adds another question
        survey_detail.add_question("How many capybara? Explain.")

        # Satisfied, she logs out
        self.browser.find_element(By.CSS_SELECTOR, "#id_logout").click()

    def test_multiple_users_can_start_questions_at_different_urls(self):
        """Multiple instructors can create surveys with unique URLs"""

        # Zhi logs in and creates a survey
        self.login("user1@example.com")

        # He's on the dashboard and creates a survey
        dashboard = InstructorDashboardPage(self)
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Zhi's Survey")

        # He adds a question
        survey_detail = InstructorSurveyDetailPage(self)
        survey_detail.add_question("How do you feel about capybara?")

        # He notices that his survey has a unique URL
        user1_survey_url = self.browser.current_url
        self.assertRegex(user1_survey_url, "/instructor/surveys/.+")

        # Now a new user, Kerrie, comes along to the site
        # We use a new browser session to simulate a new user
        self.browser.delete_all_cookies()

        # Kerrie logs in
        self.login("user2@example.com")

        # Kerrie is on her dashboard
        dashboard.wait_for_url("/instructor/")

        # Kerrie creates her own survey
        dashboard.click_create_survey()
        create_page.create_survey("Kerrie's Survey")

        # She adds a different question
        survey_detail.add_question("Why manatee? Explain.")

        # Kerrie gets her own unique URL
        user2_survey_url = self.browser.current_url
        self.assertRegex(user2_survey_url, "/instructor/surveys/.+")
        self.assertNotEqual(user2_survey_url, user1_survey_url)

        # There is no trace of Zhi's survey question
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("How do you feel about capybara?", page_text)
        self.assertIn("Why manatee? Explain.", page_text)

        # Satisfied, they both go back to sleep

    def test_instructor_can_name_their_survey(self):
        """Instructor can name their survey when creating it"""

        # Instructor logs in
        self.login("instructor@test.com")

        # She clicks "Create Survey" in the sidebar
        dashboard = InstructorDashboardPage(self)
        dashboard.click_create_survey()

        # She sees a field to name her survey
        name_input = self.browser.find_element(By.NAME, "survey_name")
        self.assertEqual(name_input.get_attribute("placeholder"), "Survey name")

        # She creates her survey
        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Q4 Capybara Evaluation")

        # Wait for the survey to be created and editor to load
        dashboard.wait_for_content("Q4 Capybara Evaluation")

        # She adds her first question
        survey_detail = InstructorSurveyDetailPage(self)
        survey_detail.add_question("How did you find the capybara?")

        # She goes to "My Surveys" via the sidebar
        dashboard.click_my_surveys()

        # She sees her survey listed by name in the main content
        dashboard.wait_for_content("Q4 Capybara Evaluation")
        main_content = self.browser.find_element(By.ID, "main-content")
        self.assertNotIn("How did you find the capybara?", main_content.text)
