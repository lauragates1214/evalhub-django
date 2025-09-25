from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time

MAX_WAIT = 5


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_question_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, "id_question_table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException):
                if time.time() - start_time > MAX_WAIT:
                    raise
                time.sleep(0.5)

    # Acts as regression test
    def test_can_start_a_new_question(self):
        # User 1 goes to the EvalHub homepage to register as a new user
        self.browser.get(self.live_server_url)

        # She notices the page title mentions EvalHub
        self.assertIn("EvalHub", self.browser.title)

        # She notices the header mentions surveys
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Survey", header_text)

        # She is invited to create a new question
        inputbox = self.browser.find_element(By.ID, "id_new_question")

        self.assertEqual(inputbox.get_attribute("placeholder"), "Enter a new question")

        # She types "Puppetry Workshop Question" into a text box
        inputbox.send_keys("How do you feel about capybara?")

        # When she hits enter, the page updates, and now the page lists
        # "1: Puppetry Workshop Question" as a question in a list of questions
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_question_table("1: How do you feel about capybara?")

        # There is still a text box inviting her to add another question.
        # She enters "PyCon UK Question" and hits enter
        inputbox = self.browser.find_element(By.ID, "id_new_question")
        inputbox.send_keys("How many capybara? Explain.")
        inputbox.send_keys(Keys.ENTER)

        # The page updates again, and now shows both questions in her list
        self.wait_for_row_in_question_table("2: How many capybara? Explain.")
        self.wait_for_row_in_question_table("1: How do you feel about capybara?")

        # Satisfied, she logs out to continue later.

    def test_multiple_users_can_start_questions_at_different_urls(self):
        # User 1 starts a new question
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element(By.ID, "id_new_question")
        inputbox.send_keys("How do you feel about capybara?")
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_question_table("1: How do you feel about capybara?")

        # She notices that her question has a unique URL
        user1_question_url = self.browser.current_url
        self.assertRegex(user1_question_url, "/surveys/.+")

        # Now a new user, User 2, comes along to the site

        ## Delete all the browser's cookies as a way of simulating a brand new user session
        self.browser.delete_all_cookies()

        # User 2 visits the home page. There is no sign of User 1's question
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("How do you feel about capybara?", page_text)

        # User 2 starts a new question by entering a new question name
        inputbox = self.browser.find_element(By.ID, "id_new_question")
        inputbox.send_keys("What is your favorite manatee? Explain.")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_question_table("What is your favorite manatee? Explain.")

        # User 2 gets their own unique URL
        user2_question_url = self.browser.current_url
        self.assertRegex(user2_question_url, "/questions/.+")
        self.assertNotEqual(user2_question_url, user1_question_url)

        # Again, there is no trace of User 1's question
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("How do you feel about capybara?", page_text)
        self.assertIn("What is your favorite manatee? Explain.", page_text)

        # Satisfied, they both go back to sleep
