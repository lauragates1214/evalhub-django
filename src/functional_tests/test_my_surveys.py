from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
)

from selenium.webdriver.common.by import By

from .base import FunctionalTest
from .container_commands import create_session_on_server
from .management.commands.create_session import (
    create_pre_authenticated_session as create_session_locally,
)

User = get_user_model()


class MySurveysTest(FunctionalTest):
    def create_pre_authenticated_session(self, email):
        if self.test_server:
            session_key = create_session_on_server(self.test_server, email)
        else:
            session_key = create_session_locally(email)

        # Set cookie in browser by visiting an arbitrary page first (404 loads fastest)
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(
            dict(
                name=settings.SESSION_COOKIE_NAME,
                value=session_key,
                path="/",
            )
        )

    def test_logged_in_users_surveys_are_saved(self):
        email = "user@example.com"

        # User1 is a logged-in user
        self.create_pre_authenticated_session(email)

        # They go to home page and create a survey
        self.browser.get(self.live_server_url)
        self.add_survey_question("What's your least favourite capybara?")
        self.add_survey_question("Why and how?")
        first_survey_url = self.browser.current_url

        # They notice a "My Surveys" link
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()

        # They see their email in the page heading
        self.wait_for(
            lambda: self.assertIn(
                email,
                self.browser.find_element(By.CSS_SELECTOR, "h1").text,
            )
        )

        # They see their survey listed, named after its first question
        self.wait_for(
            lambda: self.browser.find_element(
                By.LINK_TEXT, "What's your least favourite capybara?"
            )
        )
        self.browser.find_element(
            By.LINK_TEXT, "What's your least favourite capybara?"
        ).click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_survey_url)
        )

        # They decide to start another survey, just to see
        self.browser.get(self.live_server_url)
        self.add_survey_question("Click cows?")
        second_survey_url = self.browser.current_url

        # Under "my surveys", their new survey appears
        self.browser.find_element(By.LINK_TEXT, "My Surveys").click()
        self.wait_for(lambda: self.browser.find_element(By.LINK_TEXT, "Click cows?"))
        self.browser.find_element(By.LINK_TEXT, "Click cows?").click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_survey_url)
        )

        # They log out.  The "My Surveys" option disappears
        self.browser.find_element(By.CSS_SELECTOR, "#id_logout").click()
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_elements(By.LINK_TEXT, "My Surveys"),
                [],
            )
        )
