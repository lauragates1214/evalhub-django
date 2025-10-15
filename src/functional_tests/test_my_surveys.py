from selenium.webdriver.common.by import By

from .base import FunctionalTest
from .pages.instructor_pages import (
    InstructorDashboardPage,
    InstructorSurveyCreatePage,
    InstructorSurveyDetailPage,
)


class MySurveysTest(FunctionalTest):
    def test_logged_in_users_surveys_are_saved(self):
        # A logged-in user visits the site
        email = "user@example.com"
        self.login(email)

        # They're now on the dashboard - they click "Create Survey"
        dashboard = InstructorDashboardPage(self)
        dashboard.click_create_survey()

        # They create their first survey
        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Capybara Feedback")

        # They add a question
        survey_detail = InstructorSurveyDetailPage(self)
        survey_detail.add_question("What's your least favourite capybara?")

        # After adding questions, they navigate back to My Surveys
        dashboard.click_my_surveys()

        # They see their survey listed by the name they chose
        dashboard.wait_for_content("Capybara Feedback")

        # They create another survey
        dashboard.click_create_survey()
        create_page.create_survey("Cow Survey")

        # Add a question to the second survey
        survey_detail.add_question("Click cows?")

        # Navigate back to My Surveys
        dashboard.click_my_surveys()

        # Both surveys should be listed
        main_content = self.browser.find_element(By.ID, "main-content")
        self.wait_for(lambda: self.assertIn("Capybara Feedback", main_content.text))
        self.assertIn("Cow Survey", main_content.text)
