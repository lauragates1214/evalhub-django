from selenium.webdriver.common.by import By
from .base import FunctionalTest
from .pages.instructor_pages import InstructorDashboardPage, InstructorSurveyCreatePage
from accounts.models import User
from surveys.models import Survey


class URLRefactoringTest(FunctionalTest):
    """Test that URLs follow the new structure: /instructor/ and /student/"""

    def test_instructor_urls_use_instructor_prefix(self):
        # Zhi is an instructor who logs into EvalHub
        self.login("zhi@instructor.com")

        # After logging in, she's redirected to the instructor dashboard
        # at /instructor/ (not /dashboard/)
        dashboard = InstructorDashboardPage(self)
        dashboard.wait_for_url("/instructor/")

        # She sees the instructor navigation sidebar
        dashboard.check_sidebar_visible()

        # She clicks "My Surveys" and the URL changes to /instructor/surveys/
        dashboard.click_my_surveys()
        dashboard.wait_for_url("/instructor/surveys/")

        # She clicks "Create Survey" and the URL changes to /instructor/survey/create/
        dashboard.click_create_survey()
        dashboard.wait_for_url("/instructor/survey/create/")

        # She creates a survey
        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Capybara Survey")

        # After creation, she's taken to edit that survey at
        # /instructor/survey/<id>/
        self.wait_for(
            lambda: self.assertRegex(
                self.browser.current_url, r"/instructor/survey/{\d+/$}"
            )
        )

        # She can view responses at /instructor/survey/<id>/responses/
        survey = Survey.objects.get(owner__email="zhi@instructor.com")
        self.browser.get(
            f"{self.live_server_url}/instructor/survey/{survey.id}/responses/"
        )

        # She sees the responses page
        self.assertIn("Responses", self.browser.page_source)

    def test_student_urls_use_student_prefix(self):
        # First, create a survey for students to access
        self.login("instructor@test.com")
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor, name="Test Survey")

        # Log out the instructor
        self.browser.find_element(By.ID, "id_logout").click()

        # A student (anonymous for now) visits the survey
        # at /student/survey/<id>/
        self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

        # They see the survey page
        self.assertIn("Test Survey", self.browser.page_source)

        # The URL is /student/survey/<id>/ (not /survey/<id>/)
        self.assertEqual(
            self.browser.current_url,
            f"{self.live_server_url}/student/survey/{survey.id}/",
        )
