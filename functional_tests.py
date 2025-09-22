import unittest
from selenium import webdriver


## Scenario: As an organization admin, I want to register as a new user, so that I can manage events and questions. ##
class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_register_as_new_user(self):
        # User goes to the EvalHub homepage to register as a new user
        self.browser.get('http://localhost:8000')

        # She notices the page title and header mention EvalHub
        self.assertIn("EvalHub", self.browser.title) 
        self.assertIn("EvalHub", self.header_text)

        # She sees a link inviting her to register as a new user
        self.fail("Finish the test!")

        # She clicks it 
        # She is taken to a registration page with a form asking for:
        # Name, Email, Password, and Password confirmation

        # She fills in her details

        # She submits the form
        # The page refreshes and she is redirected to the admin dashboard

        # She sees a message confirming her registration and login

        # Satisfied that she is now able to manage surveys, she logs out to continue later.
        

if __name__ == '__main__':
    unittest.main()