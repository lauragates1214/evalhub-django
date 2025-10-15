from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class LoginPage:
    """Page object for login page"""

    def __init__(self, test):
        self.test = test

    def navigate_to_login(self):
        """Navigate to the login page"""
        self.test.browser.get(f"{self.test.live_server_url}/accounts/login/")
        return self

    def click_login_link_in_navbar(self):
        """Click the login link in the navbar"""
        login_link = self.test.browser.find_element(By.ID, "id_login_link")
        login_link.click()
        return self

    def wait_for_login_page(self):
        """Wait for the login page to load"""
        self.test.wait_for(
            lambda: self.test.assertEqual(
                self.test.browser.current_url,
                f"{self.test.live_server_url}/accounts/login/",
            )
        )
        return self

    def enter_credentials(self, email, password):
        """Enter username and password"""
        self.test.browser.find_element(By.NAME, "username").send_keys(email)
        self.test.browser.find_element(By.NAME, "password").send_keys(password)
        return self

    def submit_login(self):
        """Submit the login form by sending ENTER on password field"""
        self.test.browser.find_element(By.NAME, "password").send_keys(Keys.ENTER)
        return self

    def login(self, email, password):
        """Complete login flow: enter credentials and submit"""
        self.enter_credentials(email, password)
        self.submit_login()
        return self

    def wait_for_logged_in(self, email):
        """Wait for user to be logged in (email appears in navbar)"""
        self.test.wait_for(
            lambda: self.test.assertIn(
                email, self.test.browser.find_element(By.CSS_SELECTOR, ".navbar").text
            )
        )
        return self

    def click_logout(self):
        """Click the logout button"""
        self.test.browser.find_element(By.ID, "id_logout").click()
        return self

    def wait_for_logged_out(self):
        """Wait for logout to complete (login link visible again)"""
        self.test.wait_for(
            lambda: self.test.browser.find_element(By.ID, "id_login_link")
        )
        return self
