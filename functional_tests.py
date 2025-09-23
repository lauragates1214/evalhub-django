import unittest
from selenium import webdriver


## Scenario: As an organization admin, I want to register as a new user, so that I can manage events and questions. ##
class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_create_new_feedback_sessions(self):
        # User goes to the EvalHub homepage to register as a new user
        self.browser.get('http://localhost:8000')

        # She notices the page title and header mention EvalHub
        self.assertIn('EvalHub', self.browser.title) 

        # She is invited to create a new event
        self.fail('Finish the test!')

        # She types 'Puppetry Workshop' into a text box

        # When she hits enter, the page updates, and now the page lists
        # "1: Puppetry Workshop" as an event in a list of events

        # There is still a text box inviting her to add another event. 
        # She enters "PyCon UK 2025"

        # She hits enter again, and the page updates again,
        # and now shows both events on her event list

        # Satisfied, she logs out to continue later.


if __name__ == '__main__':
    unittest.main()