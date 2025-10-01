from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import FunctionalTest


class ItemValidationTest(FunctionalTest):
    def test_cannot_add_empty_list_items(self):
        # User 1 goes to the home page and accidentally tries to submit
        # an empty question. She hits Enter on the empty input box

        # The home page refreshes, and there is an error message saying
        # that question names cannot be blank

        # She tries again with some text for the question, which now works

        # Perversely, she now descides to submit a second blank question

        # She receives a similar warning on the question page

        # And she can correct it by filling some text in
        self.fail("Write me!")
