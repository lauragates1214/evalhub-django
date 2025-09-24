import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import unittest


## Scenario: As an organization admin, I want to register as a new user, so that I can manage surveys. ##
class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_create_new_surveys(self):
        # User goes to the EvalHub homepage to register as a new user
        self.browser.get("http://localhost:8000")

        # She notices the page title and header mention EvalHub
        self.assertIn("EvalHub", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
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
        time.sleep(1)  # wait for the page to load

        table = self.browser.find_element(By.ID, "id_survey_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn("1: Puppetry Workshop Survey", [row.text for row in rows])

        # There is still a text box inviting her to add another survey.
        # She enters "PyCon UK Survey" and hits enter
        inputbox = self.browser.find_element(By.ID, "id_new_survey")
        inputbox.send_keys("PyCon UK Survey")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)  # wait for the page to load

        # The page updates again, and now shows both surveys in her list
        table = self.browser.find_element(By.ID, "id_survey_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn("2: PyCon UK Survey", [row.text for row in rows])
        self.assertIn("1: Puppetry Workshop Survey", [row.text for row in rows])
        self.fail("Finish the test!")

        # Satisfied, she logs out to continue later.


if __name__ == "__main__":
    unittest.main()
