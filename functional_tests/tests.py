from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time

MAX_WAIT = 5


## Scenario: As an organization admin, I want to register as a new user, so that I can manage surveys. ##
class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_survey_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, "id_survey_table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException):
                if time.time() - start_time > MAX_WAIT:
                    raise
                time.sleep(0.5)

    def test_can_create_new_surveys(self):
        # User goes to the EvalHub homepage to register as a new user
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention EvalHub
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text

        self.assertIn("EvalHub", self.browser.title)
        self.assertIn("Surveys", header_text)

        # She is invited to create a new survey
        inputbox = self.browser.find_element(By.ID, "id_new_survey")

        self.assertEqual(
            inputbox.get_attribute("placeholder"), "Enter a new survey name"
        )

        # She types "Puppetry Workshop Survey" into a text box
        inputbox.send_keys("Puppetry Workshop Survey")

        # When she hits enter, the page updates, and now the page lists
        # "1: Puppetry Workshop Survey" as a survey in a list of surveys
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_survey_table("1: Puppetry Workshop Survey")

        # There is still a text box inviting her to add another survey.
        # She enters "PyCon UK Survey" and hits enter
        inputbox = self.browser.find_element(By.ID, "id_new_survey")
        inputbox.send_keys("PyCon UK Survey")
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both surveys in her list
        self.wait_for_row_in_survey_table("2: PyCon UK Survey")
        self.wait_for_row_in_survey_table("1: Puppetry Workshop Survey")

        # Satisfied, she logs out to continue later.
