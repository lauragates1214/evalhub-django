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

        # User is logged in
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)

        # Check they're logged in
        self.wait_for(
            lambda: self.assertIn(
                email, self.browser.find_element(By.CSS_SELECTOR, ".navbar").text
            )
        )
