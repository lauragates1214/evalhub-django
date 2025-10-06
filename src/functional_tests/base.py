from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import os
import time
from datetime import datetime
from pathlib import Path
from unittest import skip

from .container_commands import reset_database

MAX_WAIT = 5
SCREEN_DUMP_LOCATION = Path(__file__).absolute().parent / "screendumps"


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_fn


class FunctionalTest(StaticLiveServerTestCase):
    ### Helper methods for functional tests ###
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.test_server = os.environ.get("TEST_SERVER")
        if self.test_server:
            self.live_server_url = "http://" + self.test_server
            reset_database(self.test_server)

    def tearDown(self):
        if self._test_has_failed():
            if not SCREEN_DUMP_LOCATION.exists():
                SCREEN_DUMP_LOCATION.mkdir(parents=True)
            self.take_screenshot()
            self.dump_html()
        self.browser.quit()

    def _test_has_failed(self):
        return self._outcom

    # helper methods for taking screenshots and dumping HTML
    def take_screenshot(self):
        path = SCREEN_DUMP_LOCATION / self._get_filename("png")
        print("screenshotting to", path)
        self.browser.get_screenshot_as_file(str(path))

    def dump_html(self):
        path = SCREEN_DUMP_LOCATION / self._get_filename("html")
        print("dumping page HTML to", path)
        path.write_text(self.browser.page_source)

    def _get_filename(self, extension):
        timestamp = datetime.now().isoformat().replace(":", ".")[:19]
        return (
            f"{self.__class__.__name__}.{self._testMethodName}-{timestamp}.{extension}"
        )

    def login(self, email, password="password"):
        from django.contrib.auth import get_user_model
        from selenium.webdriver.common.keys import Keys

        if self.test_server:
            # When testing against a real server, create user on that server
            from .container_commands import create_user_on_server

            create_user_on_server(self.test_server, email, password)
        else:
            # When testing locally with LiveServerTestCase, create user in test DB
            User = get_user_model()
            user = User.objects.create(email=email)
            user.set_password(password)
            user.save()

        self.browser.get(self.live_server_url + "/accounts/login/")
        self.browser.find_element(By.NAME, "username").send_keys(email)
        self.browser.find_element(By.NAME, "password").send_keys(password, Keys.ENTER)
        self.wait_for(
            lambda: self.assertIn(
                email, self.browser.find_element(By.CSS_SELECTOR, ".navbar").text
            )
        )

    @wait
    def wait_for(self, fn):
        return fn()

    @wait
    def wait_for_row_in_question_table(self, row_text):
        table = self.browser.find_element(By.ID, "id_question_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn(row_text, [row.text for row in rows])

    def get_question_input_box(self):
        return self.browser.find_element(By.ID, "id_text")

    def add_survey_question(self, question_text):
        num_rows = len(
            self.browser.find_elements(By.CSS_SELECTOR, "#id_question_table tbody tr")
        )
        self.get_question_input_box().send_keys(question_text)
        self.get_question_input_box().send_keys(Keys.ENTER)
        question_number = num_rows + 1

        self.wait_for_row_in_question_table(f"{question_number}: {question_text}")
