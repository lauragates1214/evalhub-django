from .base import FunctionalTest
from .pages import LoginPage


class AuthenticationTest(FunctionalTest):
    def test_instructor_can_log_in(self):
        # Create a test user
        email = "instructor@example.com"
        password = "password123"
        self.create_test_user(email, password)

        # An instructor visits the site and sees a login form
        self.browser.get(self.live_server_url)

        # She sees a login link in the navbar
        login_page = LoginPage(self)
        login_page.click_login_link_in_navbar()

        # She's taken to a login page
        login_page.wait_for_login_page()

        # She enters her credentials and submits
        login_page.enter_credentials(email, password)
        login_page.submit_login()

        # She's logged in and redirected to home
        login_page.wait_for_logged_in(email)

    def test_instructor_can_log_out(self):
        # Create and log in a user
        email = "instructor@example.com"
        password = "password123"
        self.create_test_user(email, password)

        # She logs in
        login_page = LoginPage(self)
        login_page.navigate_to_login()
        login_page.login(email, password)

        # She sees her email in the navbar
        login_page.wait_for_logged_in(email)

        # She clicks logout
        login_page.click_logout()

        # She's logged out - sees login link again
        login_page.wait_for_logged_out()
