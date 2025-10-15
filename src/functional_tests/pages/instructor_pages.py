from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class InstructorDashboardPage:
    """Page object for instructor dashboard with sidebar navigation"""

    def __init__(self, test):
        self.test = test

    def navigate_to_dashboard(self):
        """Navigate to the instructor dashboard"""
        self.test.browser.get(f"{self.test.live_server_url}/instructor/")
        return self

    def get_sidebar(self):
        """Get the sidebar element"""
        return self.test.browser.find_element(By.ID, "instructor-sidebar")

    def get_main_content(self):
        """Get the main content area"""
        return self.test.browser.find_element(By.ID, "main-content")

    def check_sidebar_visible(self):
        """Verify the sidebar is visible with expected links"""
        sidebar = self.get_sidebar()
        self.test.assertIn("My Surveys", sidebar.text)
        self.test.assertIn("Create Survey", sidebar.text)
        return self

    def click_my_surveys(self):
        """Click the 'My Surveys' link in the sidebar"""
        sidebar = self.get_sidebar()
        sidebar.find_element(By.LINK_TEXT, "My Surveys").click()
        return self

    def click_create_survey(self):
        """Click the 'Create Survey' link in the sidebar"""
        sidebar = self.get_sidebar()
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()
        return self

    def wait_for_url(self, expected_url_fragment):
        """Wait for the URL to contain the expected fragment"""
        self.test.wait_for(
            lambda: self.test.assertIn(
                expected_url_fragment, self.test.browser.current_url
            )
        )
        return self

    def wait_for_content(self, expected_text):
        """Wait for text to appear in the main content area"""
        self.test.wait_for(
            lambda: self.test.assertIn(expected_text, self.get_main_content().text)
        )
        return self

    def check_content_contains(self, text):
        """Check that the main content contains specific text"""
        main_content = self.get_main_content()
        self.test.assertIn(text, main_content.text)
        return self

    def find_survey_link(self, survey_name):
        """Find and return a link to a survey by name"""
        return self.test.browser.find_element(By.LINK_TEXT, survey_name)

    def click_survey_link(self, survey_name):
        """Click on a survey link by name"""
        survey_link = self.find_survey_link(survey_name)
        survey_link.click()
        return self

    def check_sidebar_persists(self):
        """Verify sidebar is still visible (hasn't been removed by navigation)"""
        sidebar = self.get_sidebar()
        self.test.assertIn("My Surveys", sidebar.text)
        return self


class InstructorSurveyCreatePage:
    """Page object for the survey creation form"""

    def __init__(self, test):
        self.test = test

    def get_name_input(self):
        """Get the survey name input field"""
        return self.test.browser.find_element(By.NAME, "survey_name")

    def create_survey(self, name):
        """Fill in survey name and submit"""
        name_input = self.get_name_input()
        name_input.send_keys(name)
        name_input.send_keys(Keys.ENTER)
        return self

    def wait_for_name_input(self):
        """Wait for the survey name input to appear"""
        self.test.wait_for(lambda: self.get_name_input())
        return self


class InstructorSurveyDetailPage:
    """Page object for viewing/editing a specific survey"""

    def __init__(self, test):
        self.test = test

    def get_main_content(self):
        """Get the main content area"""
        return self.test.browser.find_element(By.ID, "main-content")

    def check_survey_name_visible(self, survey_name):
        """Verify the survey name appears"""
        main_content = self.get_main_content()
        self.test.assertIn(survey_name, main_content.text)
        return self

    def check_question_visible(self, question_text):
        """Verify a question appears"""
        main_content = self.get_main_content()
        self.test.assertIn(question_text, main_content.text)
        return self

    def click_view_responses(self):
        """Click the 'View Responses' link"""
        responses_link = self.test.wait_for(
            lambda: self.test.browser.find_element(By.LINK_TEXT, "View Responses")
        )
        self.test.scroll_to_and_click(responses_link)
        return self

    def check_qr_code_visible(self):
        """Verify QR code is present"""
        main_content = self.get_main_content()
        self.test.assertIn("qr-code", main_content.get_attribute("innerHTML"))
        return self

    def add_question(self, question_text):
        """Add a question to the survey"""
        # Wait for input to be ready
        self.test.wait_for(lambda: self.test.browser.find_element(By.NAME, "text"))

        # Get fresh reference and type + submit
        inputbox = self.test.browser.find_element(By.NAME, "text")
        inputbox.send_keys(question_text + Keys.ENTER)

        # Wait for the question to appear in the table (confirms page updated)
        self.test.wait_for(
            lambda: self.test.assertIn(
                question_text,
                self.test.browser.find_element(By.ID, "id_question_table").text,
            )
        )

        return self
