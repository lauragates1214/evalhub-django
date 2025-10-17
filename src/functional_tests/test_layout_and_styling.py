import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from unittest import skipIf

from .base import FunctionalTest
from .pages import (
    InstructorDashboardPage,
    InstructorSurveyCreatePage,
    InstructorSurveyDetailPage,
    StudentSurveyPage,
)
from surveys.models import Answer, Question, Submission


class LayoutAndStylingTest(FunctionalTest):
    """Test for layout and positioning of key pages"""

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_layout_and_styling(self):
        """Instructor dashboard and survey editor are nicely styled and laid out"""

        # Aya logs in
        self.login("aya@example.com")

        # She goes to the dashboard and clicks Create Survey
        dashboard = InstructorDashboardPage(self)
        dashboard.navigate_to_dashboard()
        dashboard.click_create_survey()

        # She creates a survey
        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Test Survey")

        # Wait for the survey editor to load
        survey_detail = InstructorSurveyDetailPage(self)
        self.wait_for(lambda: self.browser.find_element(By.ID, "id_text"))

        # Her browser window is set to a very specific size
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centred within the main content area, not the full window
        # With sidebar ~200px, the centre would be around (200 + (1024-200)/2) = 612px
        inputbox = self.browser.find_element(By.ID, "id_text")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            644,  # accounting for main-content padding
            delta=10,
        )

        # She adds a question
        survey_detail.add_question("testing")

        # The input is still nicely centred
        inputbox = self.browser.find_element(By.ID, "id_text")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            644,  # Centred position accounting for sidebar
            delta=10,
        )

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_student_survey_form_is_well_formatted(self):
        """Student survey page has proper spacing and form element layout"""

        # Instructor creates a survey with multiple question types
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", [])

        # Add different question types
        Question.objects.create(
            survey=survey,
            text="How would you rate this?",
            question_type="multiple_choice",
            options=["Excellent", "Good", "Fair", "Poor"],
        )
        Question.objects.create(
            survey=survey, text="Additional comments?", question_type="text"
        )
        self.logout()

        # Student visits the survey using page object
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        self.browser.set_window_size(1024, 768)

        # The form elements are visible and properly spaced
        survey_content = self.browser.find_element(By.ID, "survey-content")

        # Survey name is visible
        self.assertIn(survey.name, survey_content.text)

        # Questions are displayed
        survey_page.check_question_exists("How would you rate this?")
        survey_page.check_question_exists("Additional comments?")

        # Radio buttons are present for multiple choice
        radio_buttons = self.browser.find_elements(
            By.CSS_SELECTOR, 'input[type="radio"]'
        )
        self.assertGreater(len(radio_buttons), 0)

        # Submit button is visible at the bottom
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        self.assertTrue(submit_button.is_displayed())

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_navbar_layout_is_consistent(self):
        """Navbar displays consistently across different pages"""

        # Test login page navbar
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        navbar = self.browser.find_element(By.CSS_SELECTOR, "nav.navbar")

        # EvalHub brand is visible
        brand = self.browser.find_element(By.CLASS_NAME, "navbar-brand")
        self.assertEqual(brand.text, "EvalHub")
        self.assertTrue(brand.is_displayed())

        # Login link is present for anonymous users
        login_link = self.browser.find_element(By.ID, "id_login_link")
        self.assertTrue(login_link.is_displayed())

        # After logging in
        self.login("instructor@test.com")

        # Navbar still displays EvalHub brand
        navbar = self.browser.find_element(By.CSS_SELECTOR, "nav.navbar")
        brand = self.browser.find_element(By.CLASS_NAME, "navbar-brand")
        self.assertEqual(brand.text, "EvalHub")

        # User email is displayed
        navbar_text = navbar.text
        self.assertIn("instructor@test.com", navbar_text)

        # Logout button is present
        logout_button = self.browser.find_element(By.ID, "id_logout")
        self.assertTrue(logout_button.is_displayed())

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_dashboard_sidebar_remains_visible_during_navigation(self):
        """Sidebar persists correctly when navigating between dashboard sections"""

        # Instructor logs in
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions(
            "instructor@test.com", ["Test question"]
        )

        dashboard = InstructorDashboardPage(self)
        dashboard.navigate_to_dashboard()

        # Sidebar is visible using page object method
        dashboard.check_sidebar_visible()
        sidebar = dashboard.get_sidebar()
        sidebar_initial_location = sidebar.location

        # Click through to My Surveys
        dashboard.click_my_surveys()

        # Sidebar is still visible in same position
        dashboard.check_sidebar_visible()
        sidebar = dashboard.get_sidebar()
        self.assertEqual(sidebar.location, sidebar_initial_location)

        # Click through to a survey detail
        survey_link = dashboard.find_survey_link(survey.name)
        self.scroll_to_and_click(survey_link)

        # Sidebar still persists
        dashboard.check_sidebar_persists()

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_qr_code_displays_properly_on_survey_page(self):
        """QR code is visible and properly sized on survey detail page"""

        # Instructor creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", ["Test"])

        # Navigate to survey detail using page object
        survey_detail = InstructorSurveyDetailPage(self)
        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # Use page object to check QR code
        survey_detail.check_qr_code_visible()

        # QR code has reasonable dimensions (not too small, not too large)
        qr_code = self.browser.find_element(By.CSS_SELECTOR, "img.qr-code")
        qr_size = qr_code.size
        self.assertGreater(qr_size["width"], 100)
        self.assertLess(qr_size["width"], 500)

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_responses_list_displays_readably(self):
        """Responses list page formats data in a readable layout"""
        # Instructor creates survey and adds a response
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions(
            "instructor@test.com", ["How was it?"]
        )

        # Simulate a student response
        question = Question.objects.get(survey=survey)
        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            submission=submission, question=question, answer_text="It was great!"
        )

        # Instructor views responses
        self.browser.get(
            f"{self.live_server_url}/instructor/survey/{survey.id}/responses/"
        )

        # Survey name is displayed as heading
        dashboard = InstructorDashboardPage(self)
        main_content = dashboard.get_main_content()
        self.assertIn(survey.name, main_content.text)

        # Question and answer are displayed
        self.assertIn("How was it?", main_content.text)
        self.assertIn("It was great!", main_content.text)

    @skipIf(os.environ.get("CI"), "Visual layout testing not reliable in headless CI")
    def test_confirmation_message_displays_prominently_after_submission(self):
        """Confirmation message is clearly visible after student submits survey"""

        # Instructor creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions(
            "instructor@test.com", ["Test question"]
        )
        self.logout()

        # Student fills out survey using page object
        survey_page = StudentSurveyPage(self)
        survey_page.navigate_to_survey(survey.id)

        # Fill in response and submit using page object methods
        survey_page.fill_text_response_by_id(
            survey.question_set.first().id, "My response"
        )
        survey_page.submit()

        # Wait for confirmation using page object
        survey_page.wait_for_confirmation()

        # Confirmation message appears
        confirmation = self.browser.find_element(By.CLASS_NAME, "confirmation-message")
        self.assertTrue(confirmation.is_displayed())
        self.assertIn("Thank you", confirmation.text)

        # Form is no longer visible
        forms = self.browser.find_elements(By.TAG_NAME, "form")
        self.assertEqual(len(forms), 0)


class ButtonStylingTest(FunctionalTest):
    """Tests for button styling consistency"""

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_submit_buttons_have_consistent_styling(self):
        # Instructor logs in and creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", [])

        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # Find submit button
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )

        # Check border-radius (should be 16px)
        border_radius = submit_button.value_of_css_property("border-radius")
        self.assertEqual(border_radius, "16px")

        # Check border thickness (should be 6px)
        border_width = submit_button.value_of_css_property("border-width")
        self.assertIn("6px", border_width)

        # Check font-family includes headers font
        font_family = submit_button.value_of_css_property("font-family")
        self.assertIn("Roboto Slab", font_family)

        # Check font-weight is bold/800
        font_weight = submit_button.value_of_css_property("font-weight")
        self.assertIn(font_weight, ["700", "800", "bold"])

        # Check background colour is accent (coral-ish)
        bg_color = submit_button.value_of_css_property("background-color")
        self.assertRegex(bg_color, r"rgba?\(19[0-9], [1-9][0-9], [4-9][0-9]")

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_link_buttons_have_consistent_styling(self):
        """Link-style buttons (like 'View Responses') have proper styling"""

        # Instructor creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", ["Test"])

        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # Find the View Responses link
        view_responses_link = self.browser.find_element(By.LINK_TEXT, "View Responses")

        # Links should have appropriate styling
        font_family = view_responses_link.value_of_css_property("font-family")
        self.assertTrue(len(font_family) > 0)

        # Should be clickable and visible
        self.assertTrue(view_responses_link.is_displayed())
        self.assertTrue(view_responses_link.is_enabled())


class FormInputStylingTest(FunctionalTest):
    """Tests for form input styling consistency"""

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_text_inputs_have_rounded_borders(self):
        """Text inputs have 16px border-radius and 6px borders"""

        # Instructor creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", [])

        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # Find the question input
        text_input = self.browser.find_element(By.ID, "id_text")

        # Check border-radius (should be 16px)
        border_radius = text_input.value_of_css_property("border-radius")
        self.assertEqual(border_radius, "16px")

        # Check border thickness (should be 6px)
        border_width = text_input.value_of_css_property("border-width")
        self.assertIn("6px", border_width)

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_form_inputs_have_focus_states(self):
        """Form inputs show visual feedback when focused"""

        # Instructor creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", [])

        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        text_input = self.browser.find_element(By.ID, "id_text")

        # Get border colour before focus
        initial_border = text_input.value_of_css_property("border-color")

        # Focus the input
        text_input.click()

        # Border should change or box-shadow should appear
        focused_border = text_input.value_of_css_property("border-color")
        box_shadow = text_input.value_of_css_property("box-shadow")

        # Either border changed or box-shadow appeared
        self.assertTrue(initial_border != focused_border or box_shadow != "none")


class TypographyStylingTest(FunctionalTest):
    """Tests for typography consistency"""

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_headers_use_display_font(self):
        """Page headers use Roboto Slab font family"""

        # Instructor logs in
        self.login("instructor@test.com")

        dashboard = InstructorDashboardPage(self)
        dashboard.navigate_to_dashboard()

        # Find the main heading
        heading = self.browser.find_element(By.TAG_NAME, "h1")

        # Check it uses Roboto Slab
        font_family = heading.value_of_css_property("font-family")
        self.assertIn("Roboto Slab", font_family)

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_body_text_uses_sans_serif(self):
        """Body text uses Source Sans Pro"""

        # Visit login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")

        # Check body font
        body = self.browser.find_element(By.TAG_NAME, "body")
        font_family = body.value_of_css_property("font-family")

        # Should use Source Sans Pro or fallback sans-serif
        self.assertTrue("Source Sans Pro" in font_family or "sans-serif" in font_family)

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_survey_name_is_prominent(self):
        """Survey names are displayed prominently with appropriate heading styling"""

        # Instructor creates a survey through UI
        self.login("instructor@test.com")

        dashboard = InstructorDashboardPage(self)
        dashboard.navigate_to_dashboard()
        dashboard.click_create_survey()

        create_page = InstructorSurveyCreatePage(self)
        create_page.create_survey("Test Survey")

        # Wait for survey name to appear after HTMX swap
        self.wait_for(lambda: self.browser.find_element(By.ID, "survey-name-display"))

        # Survey name should be in an h2
        survey_name = self.browser.find_element(By.ID, "survey-name-display")

        # Should be visible and prominent
        self.assertTrue(survey_name.is_displayed())

        # Should use header font
        font_family = survey_name.value_of_css_property("font-family")
        self.assertIn("Roboto Slab", font_family)


class ColorStylingTest(FunctionalTest):
    """Tests for consistent colour usage throughout the app"""

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_primary_brand_color_on_navbar_brand(self):
        """EvalHub brand uses primary colour"""

        self.browser.get(f"{self.live_server_url}/accounts/login/")

        brand = self.browser.find_element(By.CLASS_NAME, "navbar-brand")
        color = brand.value_of_css_property("color")

        # Should be the brand forest green (dark green)
        # Expecting something like rgb(45, 90, 39) or similar
        self.assertRegex(
            color, r"rgba?\([3-5][0-9], [7-9][0-9]|1[0-2][0-9], [3-5][0-9]"
        )

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_accent_color_on_submit_buttons(self):
        """Submit buttons use accent coral colour"""

        # Instructor creates a survey
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", [])

        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        bg_color = submit_button.value_of_css_property("background-color")

        # Should be coral/orange-ish (high R, medium-high G, lower B)
        self.assertRegex(bg_color, r"rgba?\(19[0-9], [1-9][0-9], [4-9][0-9]")


class SpacingAndLayoutTest(FunctionalTest):
    """Tests for consistent spacing throughout the app"""

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_form_groups_have_consistent_spacing(self):
        """Form groups are consistently spaced"""

        # Visit login page which has multiple form groups
        self.browser.get(f"{self.live_server_url}/accounts/login/")

        # Get form inputs
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")

        # Calculate vertical distance between inputs
        username_bottom = username_input.location["y"] + username_input.size["height"]
        password_top = password_input.location["y"]
        spacing = password_top - username_bottom

        # Should have reasonable spacing (not too cramped, not too spread out)
        self.assertGreater(spacing, 10)
        self.assertLess(spacing, 100)

    @skipIf(os.environ.get("CI"), "Visual styling testing not reliable in headless CI")
    def test_card_components_have_proper_padding(self):
        """Card-style components have consistent internal padding"""

        # Instructor views responses (which should be in a card-like container)
        self.login("instructor@test.com")
        survey = self.create_survey_with_questions("instructor@test.com", ["Test"])

        question = Question.objects.get(survey=survey)
        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            submission=submission, question=question, answer_text="Response"
        )

        self.browser.get(
            f"{self.live_server_url}/instructor/survey/{survey.id}/responses/"
        )

        dashboard = InstructorDashboardPage(self)
        main_content = dashboard.get_main_content()

        # Content should have padding (not flush against edges)
        padding = main_content.value_of_css_property("padding")
        self.assertNotEqual(padding, "0px")
