from selenium import webdriver
from selenium.webdriver.common.by import By

from .base import FunctionalTest


def quit_if_possible(browser):
    try:
        browser.quit()
    except:
        pass


class SharingTest(FunctionalTest):
    def test_can_share_a_survey_with_another_user(self):
        # User 1 is a logged-in user
        self.login("user1@example.com")
        user1_browser = self.browser
        self.addCleanup(
            lambda: quit_if_possible(user1_browser)
        )  # cleanup if test fails

        # Her friend User 2 is also hanging out on the surveys site
        user2_browser = webdriver.Firefox()
        self.addCleanup(
            lambda: quit_if_possible(user2_browser)
        )  # cleanup if test fails
        self.browser = user2_browser
        self.login("user2@example.com")

        # User 1 goes to the home page and starts a survey
        self.browser = user1_browser
        self.browser.get(self.live_server_url)
        self.add_survey_question("Should we collaborate on this survey?")

        # She notices a "Share this survey" option
        share_box = self.browser.find_element(By.CSS_SELECTOR, 'input[name="sharee"]')
        self.assertEqual(
            share_box.get_attribute("placeholder"),
            "co-instructor@example.com",
        )
