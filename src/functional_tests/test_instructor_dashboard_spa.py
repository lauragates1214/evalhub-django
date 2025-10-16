from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest
from .pages import (
    InstructorDashboardPage,
    InstructorSurveyCreatePage,
    InstructorSurveyDetailPage,
)


class InstructorDashboardSPATest(FunctionalTest):
    """Tests for the instructor dashboard SPA-like navigation experience"""

    def test_instructor_experiences_spa_like_navigation(self):
        """Instructor navigates between dashboard sections with sidebar persisting and only main content updating without full page reloads."""

        # Zhi is an instructor who logs into EvalHub
        self.login("zhi@instructor.com")

        # After logging in, she's taken to her dashboard
        # which has a persistent navigation sidebar and main content area
        dashboard = InstructorDashboardPage(self)
        dashboard.wait_for_url("/instructor/")

        # She sees a navigation sidebar that won't disappear during navigation
        dashboard.check_sidebar_visible()

        # The main content area shows a welcome message by default
        dashboard.check_content_contains("Welcome to your dashboard")

        # She clicks "Create Survey" in the sidebar
        dashboard.click_create_survey()

        # The page doesn't reload - only the main content area changes
        # The sidebar is still there unchanged
        dashboard.wait_for_content("Create New Survey")

        # Verify the sidebar is still present and unchanged
        dashboard.check_sidebar_visible()

        # The URL has changed to reflect the new view
        dashboard.wait_for_url("/instructor/survey/create/")

        # She creates a survey with a name
        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Mid-term Feedback")

        # After creating, the main content updates to show the survey editor
        # Still no full page reload - sidebar remains
        dashboard.wait_for_content("Mid-term Feedback")

        # She clicks "My Surveys" to go back to the list
        dashboard.click_my_surveys()

        # Again, only the content area updates - showing her new survey in the list
        dashboard.wait_for_content("Mid-term Feedback")

        # The sidebar never flickered or reloaded throughout the entire experience
        dashboard.check_sidebar_visible()

    def test_my_surveys_navigation_shows_user_surveys(self):
        """Instructor can navigate to 'My Surveys' and see their surveys listed without full page reloads."""

        # Zhi logs in and creates two surveys
        self.login("zhi@instructor.com")

        # She's on the dashboard
        dashboard = InstructorDashboardPage(self)
        dashboard.wait_for_url("/instructor/")

        # She creates her first survey via the UI
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("First Survey")

        # She goes back to My Surveys
        dashboard.click_my_surveys()

        # She sees her survey listed
        dashboard.wait_for_content("First Survey")

        # She creates another survey
        dashboard.click_create_survey()
        create_page.create_survey("Second Survey")

        # Goes back to My Surveys again
        dashboard.click_my_surveys()

        # Wait for the survey list to load (not just check immediately)
        dashboard.wait_for_content("Your Surveys")

        # Then check both surveys are listed
        dashboard.check_content_contains("First Survey")
        dashboard.check_content_contains("Second Survey")

        # The sidebar never reloaded
        dashboard.check_sidebar_visible()

    def test_can_view_survey_in_dashboard(self):
        """Instructor can click on a survey from 'My Surveys' and view its details in the main content area without full page reloads."""

        # Zhi is an instructor with an existing survey
        self.login("zhi@instructor.com")

        # He's on the dashboard
        dashboard = InstructorDashboardPage(self)
        dashboard.wait_for_url("/instructor/")

        # He creates a survey first
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Chemistry Feedback")

        # He adds a question to the survey
        survey_detail = InstructorSurveyDetailPage(self)
        survey_detail.add_question("Rate the lab session")

        # He navigates to My Surveys
        dashboard.click_my_surveys()

        # He sees his survey listed and clicks on it
        dashboard.wait_for_content("Chemistry Feedback")
        dashboard.click_survey_link("Chemistry Feedback")

        # The survey loads in the main content area (not a new page)
        # He's still in the dashboard
        self.assertIn("/instructor/", self.browser.current_url)

        # He sees the survey details and can add more questions
        survey_detail.check_survey_name_visible("Chemistry Feedback")
        survey_detail.check_question_visible("Rate the lab session")

        # He can still see the sidebar (htmx swapped only the main content)
        dashboard.check_sidebar_persists()

        # He sees the QR code for the survey
        survey_detail.check_qr_code_visible()

        # He sees links for viewing responses and exporting
        main_content = dashboard.get_main_content()
        self.assertIn("View Responses", main_content.text)
        self.assertIn("Export to CSV", main_content.text)

    def test_can_view_responses_in_dashboard(self):
        """Instructor can view survey responses from the survey detail page without full page reloads."""

        # Amy is an instructor who wants to view survey responses
        self.login("amy@instructor.com")

        # She has an existing survey with responses (create via helper)
        survey = self.create_survey_with_questions(
            "amy@instructor.com", ["How was the lecture?", "Any feedback?"]
        )
        survey.name = "Chemistry 101"
        survey.save()

        # Create some test responses
        from surveys.models import Submission, Answer

        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=survey.question_set.first(),
            answer_text="Very clear",
            submission=submission,
        )

        # Amy navigates to her survey in the dashboard
        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # She sees the View Responses link and clicks it
        survey_detail = InstructorSurveyDetailPage(self)
        survey_detail.click_view_responses()

        # The responses load in the main content area - she's still in the dashboard
        self.wait_for(lambda: self.assertIn("/instructor/", self.browser.current_url))

        # She can see the response data with proper title
        dashboard = InstructorDashboardPage(self)
        dashboard.wait_for_content(f"{survey.name} Responses")

        # She sees the questions and their responses
        main_content = dashboard.get_main_content()
        self.assertIn("How was the lecture?", main_content.text)
        self.assertIn("Very clear", main_content.text)
        self.assertIn("Any feedback?", main_content.text)

        # The sidebar is still visible - no full page reload happened
        dashboard.check_sidebar_persists()

    def test_instructor_can_edit_survey_name(self):
        """Instructor can edit the survey name inline from the survey detail view without full page reloads."""

        # Emma logs in as an instructor
        self.login("emma@instructor.com")

        # She creates a survey first
        dashboard = InstructorDashboardPage(self)
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Initial Survey Name")

        # Wait for the survey editor to load
        dashboard.wait_for_content("Initial Survey Name")

        # She sees the survey name displayed and notices she can edit it
        # There should be an edit button or the name should be clickable
        survey_name_element = self.browser.find_element(By.ID, "survey-name-display")
        self.assertEqual(survey_name_element.text, "Initial Survey Name")

        # She clicks on the survey name or an edit button to make it editable
        edit_button = self.browser.find_element(By.ID, "edit-survey-name-btn")
        edit_button.click()

        # The survey name becomes an input field
        survey_name_input = self.wait_for(
            lambda: self.browser.find_element(By.ID, "survey-name-input")
        )

        # She clears the field and enters a new name
        survey_name_input.clear()
        survey_name_input.send_keys("Updated Survey Name")

        # She saves the change (either by pressing Enter or clicking Save)
        survey_name_input.send_keys(Keys.ENTER)

        # The page updates to show the new name
        dashboard.wait_for_content("Updated Survey Name")

        # The input field disappears and the name is shown as text again
        survey_name_display = self.browser.find_element(By.ID, "survey-name-display")
        self.assertEqual(survey_name_display.text, "Updated Survey Name")

        # She navigates to "My Surveys" to verify the change persisted
        dashboard.click_my_surveys()

        dashboard.wait_for_content("Updated Survey Name")

        # The old name should not appear
        main_content = dashboard.get_main_content()
        self.assertNotIn("Initial Survey Name", main_content.text)
