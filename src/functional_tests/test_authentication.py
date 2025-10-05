from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class AuthenticationTest(FunctionalTest):
    def test_instructor_can_log_in(self):
        # Create a test user
        email = "instructor@example.com"
        password = "password123"

        if self.test_server:
            from functional_tests.container_commands import create_user_on_server

            create_user_on_server(self.test_server, email, password)
        else:
            from accounts.models import User

            user = User.objects.create(email=email)
            user.set_password(password)
            user.save()

        # An instructor visits the site and sees a login form
        self.browser.get(self.live_server_url)

        # She sees a login link in the navbar
        login_link = self.browser.find_element(By.ID, "id_login_link")
        login_link.click()

        # She's taken to a login page
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.current_url, self.live_server_url + "/accounts/login/"
            )
        )

        # She enters her credentials
        self.browser.find_element(By.NAME, "username").send_keys(email)  # Changed
        self.browser.find_element(By.NAME, "password").send_keys(
            password, Keys.ENTER
        )  # Changed

        # She's logged in and redirected to home
        self.wait_for(
            lambda: self.assertIn(
                email,  # Also change this to use the variable
                self.browser.find_element(By.CSS_SELECTOR, ".navbar").text,
            )
        )

    def test_instructor_can_log_out(self):
        # Create and log in a user
        email = "instructor@example.com"
        password = "password123"

        if self.test_server:
            from functional_tests.container_commands import create_user_on_server

            create_user_on_server(self.test_server, email, password)
        else:
            from accounts.models import User

            user = User.objects.create(email=email)
            user.set_password(password)
            user.save()

        self.browser.get(self.live_server_url + "/accounts/login/")
        self.browser.find_element(By.NAME, "username").send_keys(email)
        self.browser.find_element(By.NAME, "password").send_keys(password, Keys.ENTER)

        # She sees her email in the navbar
        self.wait_for(
            lambda: self.assertIn(
                "instructor@example.com",
                self.browser.find_element(By.CSS_SELECTOR, ".navbar").text,
            )
        )

        # She clicks logout
        self.browser.find_element(By.ID, "id_logout").click()

        # She's logged out - sees login link again
        self.wait_for(lambda: self.browser.find_element(By.ID, "id_login_link"))
