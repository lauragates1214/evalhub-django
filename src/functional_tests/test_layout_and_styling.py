import os
from unittest import skipIf

from .base import FunctionalTest
from .survey_page import SurveyPage


class LayoutAndStylingTest(FunctionalTest):
    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_layout_and_styling(self):
        # User 1 logs in
        self.login("user@example.com")

        # She goes to the home page
        survey_page = SurveyPage(self).go_to_new_survey_page()

        # Her browser window is set to a very specific size
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        inputbox = survey_page.get_question_input_box()
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            512,
            delta=10,
        )

        # She starts a new survey and sees the input is nicely centered there too
        survey_page.add_survey_question("testing")
        inputbox = survey_page.get_question_input_box()
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            512,
            delta=10,
        )
