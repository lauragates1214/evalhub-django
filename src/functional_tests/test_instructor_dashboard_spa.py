from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest
from accounts.models import User
from surveys.models import Survey


class InstructorDashboardSPATest(FunctionalTest):
    def test_instructor_experiences_spa_like_navigation(self):
        # Zhi is an instructor who logs into EvalHub
        self.login("zhi@instructor.com")

        # After logging in, she's taken to her dashboard
        # which has a persistent navigation sidebar and main content area
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.current_url, self.live_server_url + "/instructor/"
            )
        )

        # She sees a navigation sidebar that won't disappear during navigation
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)
        self.assertIn("Create Survey", sidebar.text)

        # The main content area shows a welcome message by default
        main_content = self.browser.find_element(By.ID, "main-content")
        self.assertIn("Welcome to your dashboard", main_content.text)

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
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)

        # The URL has changed to reflect the new view
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + "/instructor/surveys/create/",
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
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("Create Survey", sidebar.text)

    def test_my_surveys_navigation_shows_user_surveys(self):
        # Zhi logs in and creates two surveys
        self.login("zhi@instructor.com")

        # She's on the dashboard
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.current_url, self.live_server_url + "/instructor/"
            )
        )

        # She creates her first survey via the UI
        create_link = self.browser.find_element(By.LINK_TEXT, "Create Survey")
        create_link.click()

        survey_name_input = self.browser.find_element(By.NAME, "survey_name")
        survey_name_input.send_keys("First Survey")
        survey_name_input.send_keys(Keys.ENTER)

        # She goes back to My Surveys
        my_surveys_link = self.browser.find_element(By.LINK_TEXT, "My Surveys")
        my_surveys_link.click()

        # She sees her survey listed
        self.wait_for(
            lambda: self.assertIn(
                "First Survey", self.browser.find_element(By.ID, "main-content").text
            )
        )

        # She creates another survey
        create_link = self.browser.find_element(By.LINK_TEXT, "Create Survey")
        create_link.click()

        survey_name_input = self.browser.find_element(By.NAME, "survey_name")
        survey_name_input.send_keys("Second Survey")
        survey_name_input.send_keys(Keys.ENTER)

        # Goes back to My Surveys again
        my_surveys_link = self.browser.find_element(By.LINK_TEXT, "My Surveys")
        my_surveys_link.click()

        # Wait for the survey list to load (not just check immediately)
        self.wait_for(
            lambda: self.assertIn(
                "Your Surveys",  # Check for the heading first
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # Then check both surveys are listed
        main_content = self.browser.find_element(By.ID, "main-content")
        self.assertIn("First Survey", main_content.text)
        self.assertIn("Second Survey", main_content.text)

        # The sidebar never reloaded
        self.assertTrue(self.browser.find_element(By.ID, "instructor-sidebar"))

    def test_can_view_survey_in_dashboard(self):
        # Zhi is an instructor with an existing survey
        self.login("zhi@instructor.com")

        # He's on the dashboard
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.current_url, self.live_server_url + "/instructor/"
            )
        )

        # He creates a survey first
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        name_input = self.browser.find_element(By.NAME, "survey_name")
        name_input.send_keys("Chemistry Feedback")
        name_input.send_keys(Keys.ENTER)

        # He adds a question to the survey
        self.wait_for(lambda: self.browser.find_element(By.NAME, "text"))
        inputbox = self.browser.find_element(By.NAME, "text")
        inputbox.send_keys("Rate the lab session")
        inputbox.send_keys(Keys.ENTER)

        # He navigates to My Surveys
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "My Surveys").click()

        # He sees his survey listed and clicks on it
        self.wait_for(
            lambda: self.assertIn(
                "Chemistry Feedback",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # He clicks on the survey name
        survey_link = self.browser.find_element(By.LINK_TEXT, "Chemistry Feedback")
        survey_link.click()

        # The survey loads in the main content area (not a new page)
        # He's still in the dashboard
        self.assertIn("/instructor/", self.browser.current_url)

        # He sees the survey details and can add more questions
        main_content = self.browser.find_element(By.ID, "main-content")
        self.wait_for(lambda: self.assertIn("Chemistry Feedback", main_content.text))
        self.assertIn("Rate the lab session", main_content.text)

        # He can still see the sidebar (htmx swapped only the main content)
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)

        # He sees the QR code for the survey
        self.assertIn("qr-code", main_content.get_attribute("innerHTML"))

        # He sees links for viewing responses and exporting
        self.assertIn("View Responses", main_content.text)
        self.assertIn("Export to CSV", main_content.text)

    def test_can_view_responses_in_dashboard(self):
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
        self.browser.get(f"{self.live_server_url}/instructor/surveys/{survey.id}/")

        # She sees the View Responses link and clicks it
        # Use wait_for to both wait for and return the element
        responses_link = self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, "View Responses")
        )
        # Click using JavaScript to bypass visibility checks
        self.browser.execute_script("arguments[0].click();", responses_link)

        # The responses load in the main content area - she's still in the dashboard
        self.wait_for(lambda: self.assertIn("/instructor/", self.browser.current_url))

        # She can see the response data with proper title
        main_content = self.browser.find_element(By.ID, "main-content")
        self.wait_for(
            lambda: self.assertIn(f"{survey.name} Responses", main_content.text)
        )

        # She sees the questions and their responses
        self.assertIn("How was the lecture?", main_content.text)
        self.assertIn("Very clear", main_content.text)
        self.assertIn("Any feedback?", main_content.text)

        # The sidebar is still visible - no full page reload happened
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)

    def test_instructor_can_edit_survey_name(self):
        # Emma logs in as an instructor
        self.login("emma@instructor.com")

        # She creates a survey first
        self.browser.find_element(By.LINK_TEXT, "Create Survey").click()

        survey_name_input = self.browser.find_element(By.NAME, "survey_name")
        survey_name_input.send_keys("Initial Survey Name")
        survey_name_input.send_keys(Keys.ENTER)

        # Wait for the survey editor to load
        self.wait_for(
            lambda: self.assertIn(
                "Initial Survey Name",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

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
        # Or: self.browser.find_element(By.ID, "save-survey-name-btn").click()

        # The page updates to show the new name
        self.wait_for(
            lambda: self.assertIn(
                "Updated Survey Name",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )

        # The input field disappears and the name is shown as text again
        survey_name_display = self.browser.find_element(By.ID, "survey-name-display")
        self.assertEqual(survey_name_display.text, "Updated Survey Name")

        # She navigates to "My Surveys" to verify the change persisted
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()

        self.wait_for(
            lambda: self.assertIn(
                "Updated Survey Name",
                self.browser.find_element(By.ID, "main-content").text,
            )
        )
        # The old name should not appear
        self.assertNotIn(
            "Initial Survey Name", self.browser.find_element(By.ID, "main-content").text
        )
