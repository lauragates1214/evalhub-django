from selenium.webdriver.common.by import By
from .base import FunctionalTest


class NoAnalyticsFeatureTest(FunctionalTest):

    def test_instructor_dashboard_has_no_analytics_option(self):
        # Sarah logs in as an instructor
        self.login("sarah@instructor.com")

        # She goes to her dashboard
        self.browser.get(f"{self.live_server_url}/instructor/")

        # She looks at the sidebar navigation
        sidebar = self.browser.find_element(By.ID, "instructor-sidebar")
        sidebar_text = sidebar.text

        # She notices there are survey management options
        self.assertIn("My Surveys", sidebar_text)
        self.assertIn("Create Survey", sidebar_text)

        # But there's no analytics option available
        self.assertNotIn("Analytics", sidebar_text)
        self.assertNotIn("analytics", sidebar_text.lower())

    def test_cannot_access_analytics_url_directly(self):
        # Tom logs in as an instructor
        self.login("tom@instructor.com")

        # He somehow knows about an old analytics URL and tries to access it
        self.browser.get(f"{self.live_server_url}/instructor/analytics/")

        # He gets a 404 error because this feature doesn't exist
        self.assertIn("Not Found", self.browser.page_source)

    def test_survey_detail_shows_response_viewing_not_analytics(self):
        # Emma logs in and creates a survey
        self.login("emma@instructor.com")

        from accounts.models import User
        from surveys.models import Survey, Question

        instructor = User.objects.get(email="emma@instructor.com")
        survey = Survey.objects.create(name="Student Feedback", owner=instructor)
        Question.objects.create(survey=survey, text="How was the course?")

        # She views her survey
        self.browser.get(f"{self.live_server_url}/instructor/surveys/{survey.id}/")

        # She sees options to view responses
        self.assertIn("View Responses", self.browser.page_source)

        # But no mention of analytics or data analysis
        self.assertNotIn("Analytics", self.browser.page_source)
        self.assertNotIn("Analyze", self.browser.page_source)
        self.assertNotIn("Statistics", self.browser.page_source)

    def test_response_page_shows_raw_data_not_analytics(self):
        # Ahmed logs in
        self.login("ahmed@instructor.com")

        from accounts.models import User
        from surveys.models import Survey, Question, Submission, Answer

        instructor = User.objects.get(email="ahmed@instructor.com")
        survey = Survey.objects.create(name="Workshop Feedback", owner=instructor)
        q = Question.objects.create(survey=survey, text="Rate the workshop")

        # Create a response
        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=q, answer_text="Excellent", submission=submission
        )

        # He views the responses
        self.browser.get(
            f"{self.live_server_url}/instructor/surveys/{survey.id}/responses/"
        )

        # He sees the raw responses listed
        self.assertIn("Workshop Feedback Responses", self.browser.page_source)
        self.assertIn("Rate the workshop", self.browser.page_source)
        self.assertIn("Excellent", self.browser.page_source)

        # But there are no analytics features like charts, averages, or statistics
        self.assertNotIn("Average", self.browser.page_source)
        self.assertNotIn("Chart", self.browser.page_source)
        self.assertNotIn("Graph", self.browser.page_source)
        self.assertNotIn("Statistics", self.browser.page_source)
        self.assertNotIn("Analysis", self.browser.page_source)
