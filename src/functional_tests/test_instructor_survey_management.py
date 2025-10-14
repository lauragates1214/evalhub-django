from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base import FunctionalTest
from surveys.models import Survey, Question, Submission, Answer
from accounts.models import User


class InstructorSurveyManagementTest(FunctionalTest):

    def test_cannot_add_duplicate_questions_to_survey(self):
        # Sarah logs in as an instructor
        self.login("sarah@instructor.com")

        # She creates a new survey
        self.browser.get(f"{self.live_server_url}/instructor/")
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        name_input = self.wait_for(
            lambda: self.browser.find_element(By.NAME, "survey_name")
        )
        name_input.send_keys("Student Feedback")
        name_input.send_keys(Keys.ENTER)

        # She adds a question
        question_input = self.wait_for(
            lambda: self.browser.find_element(By.NAME, "text")
        )
        question_input.send_keys("What did you think of the course?")
        question_input.send_keys(Keys.ENTER)

        # She sees the question appear in the table
        self.wait_for(
            lambda: self.assertIn(
                "1: What did you think of the course?",
                self.browser.find_element(By.ID, "id_question_table").text,
            )
        )

        # She accidentally tries to add the same question again
        question_input = self.browser.find_element(By.NAME, "text")
        question_input.send_keys("What did you think of the course?")
        question_input.send_keys(Keys.ENTER)

        # She sees an error message
        self.wait_for(
            lambda: self.assertIn(
                "You've already got this question in your survey",
                self.browser.page_source,
            )
        )

        # The duplicate question was not added
        table = self.browser.find_element(By.ID, "id_question_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertEqual(len(rows), 1)

    def test_questions_appear_in_order_they_were_added(self):
        # Tom logs in
        self.login("tom@instructor.com")

        # He creates a survey through the UI
        self.browser.get(f"{self.live_server_url}/instructor/")
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        name_input = self.wait_for(
            lambda: self.browser.find_element(By.NAME, "survey_name")
        )
        name_input.send_keys("Course Evaluation")
        name_input.send_keys(Keys.ENTER)

        # He adds questions in a specific order
        question_input = self.wait_for(
            lambda: self.browser.find_element(By.NAME, "text")
        )

        questions = ["One capybara?", "Two capybara?", "No capybara?"]
        for i, q_text in enumerate(questions, 1):
            question_input = self.browser.find_element(By.NAME, "text")
            question_input.send_keys(q_text)
            question_input.send_keys(Keys.ENTER)

            # Wait for the question to appear
            self.wait_for(
                lambda: self.assertIn(
                    f"{i}: {q_text}",
                    self.browser.find_element(By.ID, "id_question_table").text,
                )
            )

        # Verify all questions are in the correct order
        table_text = self.browser.find_element(By.ID, "id_question_table").text
        self.assertIn("1: One capybara?", table_text)
        self.assertIn("2: Two capybara?", table_text)
        self.assertIn("3: No capybara?", table_text)

        # Check that they appear in the right sequence
        pos1 = table_text.find("1: One capybara?")
        pos2 = table_text.find("2: Two capybara?")
        pos3 = table_text.find("3: No capybara?")
        self.assertLess(pos1, pos2)
        self.assertLess(pos2, pos3)

    def test_navigation_updates_content_without_losing_sidebar(self):
        # Jaydean logs in
        self.login("jaydean@instructor.com")

        # She's on the dashboard
        self.browser.get(f"{self.live_server_url}/instructor/")

        # She sees the sidebar
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)
        self.assertIn("Create Survey", sidebar.text)

        # She clicks Create Survey
        sidebar.find_element(By.LINK_TEXT, "Create Survey").click()

        # The URL updates
        self.wait_for(
            lambda: self.assertIn(
                "/instructor/surveys/create", self.browser.current_url
            )
        )

        # The sidebar is still visible
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)

        # She creates a survey
        name_input = self.wait_for(
            lambda: self.browser.find_element(By.NAME, "survey_name")
        )
        name_input.send_keys("Test Survey")
        name_input.send_keys(Keys.ENTER)

        # URL updates to show the new survey
        self.wait_for(
            lambda: self.assertIn("/instructor/surveys/", self.browser.current_url)
        )

        # Sidebar is still there
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)

    def test_cannot_access_another_instructors_survey(self):
        # Alice creates a survey (using helper to bypass UI)
        alice = User.objects.create_user(
            email="alice@instructor.com", password="password"
        )
        alice_survey = Survey.objects.create(name="Alice's Private Survey", owner=alice)

        # Bob logs in
        self.login("bob@instructor.com")

        # Bob tries to directly access Alice's survey
        self.browser.get(
            f"{self.live_server_url}/instructor/surveys/{alice_survey.id}/"
        )

        # He cannot see the survey content
        self.assertIn("403", self.browser.page_source)


class InstructorViewResponsesTest(FunctionalTest):

    def test_can_view_survey_responses_with_comments(self):
        # Mahmoud logs in
        self.login("mahmoud@instructor.com")

        # He has a survey with responses (created via helper)
        instructor = User.objects.get(email="mahmoud@instructor.com")
        survey = Survey.objects.create(name="Workshop Feedback", owner=instructor)

        q1 = Question.objects.create(
            survey=survey,
            text="Rate the workshop",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )
        q2 = Question.objects.create(
            survey=survey, text="What did you enjoy most?", question_type="text"
        )

        # Create responses
        submission1 = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=q1,
            answer_text="5",
            comment_text="Excellent presentation!",
            submission=submission1,
        )
        Answer.objects.create(
            question=q2, answer_text="The hands-on exercises", submission=submission1
        )

        submission2 = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=q1,
            answer_text="4",
            comment_text="Good but too fast",
            submission=submission2,
        )

        # Mahmoud navigates to the survey
        self.browser.get(f"{self.live_server_url}/instructor/surveys/{survey.id}/")

        # He clicks View Responses
        responses_link = self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, "View Responses")
        )
        self.scroll_to_and_click(responses_link)

        # He sees the responses organized by question
        self.wait_for(
            lambda: self.assertIn(
                "Workshop Feedback Responses", self.browser.page_source
            )
        )

        # First question and its answers
        page_content = self.browser.page_source
        self.assertIn("Rate the workshop", page_content)
        self.assertIn("5", page_content)
        self.assertIn("Excellent presentation!", page_content)
        self.assertIn("4", page_content)
        self.assertIn("Good but too fast", page_content)

        # Second question and its answer
        self.assertIn("What did you enjoy most?", page_content)
        self.assertIn("The hands-on exercises", page_content)

    def test_cannot_view_responses_for_another_instructors_survey(self):
        # Jane has a survey with responses
        jane = User.objects.create_user(
            email="jane@instructor.com", password="password"
        )
        jane_survey = Survey.objects.create(name="Jane's Survey", owner=jane)

        # John logs in
        self.login("john@instructor.com")

        # John tries to view Jane's survey responses
        self.browser.get(
            f"{self.live_server_url}/instructor/surveys/{jane_survey.id}/responses/"
        )

        # He gets an error
        self.assertIn("403", self.browser.page_source)

    def test_404_when_viewing_responses_for_nonexistent_survey(self):
        # Aya logs in
        self.login("kate@instructor.com")

        # She tries to view responses for a survey that doesn't exist
        self.browser.get(f"{self.live_server_url}/instructor/surveys/99999/responses/")

        # She sees a 404 error
        self.assertIn("Not Found", self.browser.page_source)

    def test_survey_with_no_responses_shows_empty_state(self):
        # Lisa logs in
        self.login("lisa@instructor.com")

        # She has a survey with no responses
        instructor = User.objects.get(email="lisa@instructor.com")
        survey = Survey.objects.create(name="New Survey", owner=instructor)
        Question.objects.create(survey=survey, text="First question")

        # She views the responses page
        self.browser.get(
            f"{self.live_server_url}/instructor/surveys/{survey.id}/responses/"
        )

        # She sees the survey name and question
        self.wait_for(
            lambda: self.assertIn("New Survey Responses", self.browser.page_source)
        )
        self.assertIn("First question", self.browser.page_source)

        # But there are no answer items in the list
        main_content = self.browser.find_element(By.ID, "main-content")
        response_lists = main_content.find_elements(By.CSS_SELECTOR, "ul")
        for ul in response_lists:
            list_items = ul.find_elements(By.TAG_NAME, "li")
            # The response list should be empty (no responses)
            self.assertEqual(len(list_items), 0)

    def test_responses_load_via_sidebar_navigation(self):
        # Igor logs in
        self.login("igor@instructor.com")

        # He has a survey with a response
        instructor = User.objects.get(email="igor@instructor.com")
        survey = Survey.objects.create(name="Quick Poll", owner=instructor)
        q = Question.objects.create(survey=survey, text="Your feedback?")
        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=q, answer_text="Great session", submission=submission
        )

        # He starts at the dashboard
        self.browser.get(f"{self.live_server_url}/instructor/")

        # He navigates to My Surveys via sidebar
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar.find_element(By.LINK_TEXT, "My Surveys").click()

        # He sees his survey listed
        self.wait_for(lambda: self.assertIn("Quick Poll", self.browser.page_source))

        # He clicks on the survey
        survey_link = self.browser.find_element(By.LINK_TEXT, "Quick Poll")
        survey_link.click()

        # He sees the survey detail with View Responses link
        self.wait_for(lambda: self.assertIn("View Responses", self.browser.page_source))

        # He clicks View Responses
        responses_link = self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, "View Responses")
        )
        self.scroll_to_and_click(responses_link)

        # The URL updates to show responses
        self.wait_for(lambda: self.assertIn("/responses/", self.browser.current_url))

        # The sidebar is still visible (no full page reload)
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        self.assertIn("My Surveys", sidebar.text)

        # He sees the response
        self.assertIn("Quick Poll Responses", self.browser.page_source)
        self.assertIn("Your feedback?", self.browser.page_source)
        self.assertIn("Great session", self.browser.page_source)
