from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class AuthenticationTest(FunctionalTest):
    def test_instructor_can_log_in(self):
        # Create a test user
        from accounts.models import User

        user = User.objects.create(email="instructor@example.com")
        user.set_password("password123")
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
        self.browser.find_element(By.NAME, "username").send_keys(
            "instructor@example.com"
        )
        self.browser.find_element(By.NAME, "password").send_keys(
            "password123", Keys.ENTER
        )

        # She's logged in and redirected to home
        self.wait_for(
            lambda: self.assertIn(
                "instructor@example.com",
                self.browser.find_element(By.CSS_SELECTOR, ".navbar").text,
            )
        )
