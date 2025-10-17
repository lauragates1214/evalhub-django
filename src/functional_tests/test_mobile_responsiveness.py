from selenium.webdriver.common.by import By

from .base import FunctionalTest
from .pages.auth_pages import LoginPage


class MobileResponsivenessTest(FunctionalTest):
    """Functional tests to verify mobile-responsive design on key pages"""

    def test_mobile_viewport_on_login_page(self):
        """Login page is properly responsive on mobile screen sizes"""

        # Set browser to mobile viewport (iPhone SE size)
        self.browser.set_window_size(375, 667)

        # A student visits the login page on their phone
        login_page = LoginPage(self)
        login_page.navigate_to_login()

        # The page has a viewport meta tag for mobile responsiveness
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, 'meta[name="viewport"]')
        )
        viewport_meta = self.browser.find_element(
            By.CSS_SELECTOR, 'meta[name="viewport"]'
        )
        self.assertIn("width=device-width", viewport_meta.get_attribute("content"))

        # Form inputs are not too wide for the screen
        email_input = self.browser.find_element(By.NAME, "username")
        input_width = email_input.size["width"]
        viewport_width = self.browser.execute_script("return window.innerWidth")

        # Input should not exceed 90% of viewport width (allowing for padding)
        self.assertLess(input_width, viewport_width * 0.9)

        # Touch targets (buttons) are large enough for comfortable tapping
        # Minimum recommended is 44px
        login_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        button_height = login_button.size["height"]
        self.assertGreaterEqual(
            button_height,
            44,
            f"Button height {button_height}px is below minimum 44px for touch targets",
        )

    def test_mobile_has_optimised_styles(self):
        """Form inputs have mobile-optimised borders and padding on small screens"""

        # Set browser to mobile viewport (iPhone SE size)
        self.browser.set_window_size(375, 667)

        # A student visits the login page on their phone
        login_page = LoginPage(self)
        login_page.navigate_to_login()

        # Form inputs should have thinner borders on mobile (4px or less)
        email_input = self.browser.find_element(By.NAME, "username")
        border_width = email_input.value_of_css_property("border-width")
        border_px = int(border_width.replace("px", ""))

        self.assertLessEqual(
            border_px,
            4,
            f"Border width {border_px}px is too thick for mobile (should be ≤4px)",
        )

        # Padding should be smaller on mobile (12px or less)
        padding = email_input.value_of_css_property("padding")
        padding_px = int(padding.split()[0].replace("px", ""))

        self.assertLessEqual(
            padding_px,
            12,
            f"Padding {padding_px}px is too large for mobile (should be ≤12px)",
        )

    def test_mobile_buttons_have_optimised_styles(self):
        """Submit buttons have mobile-optimised padding on small screens"""

        # Set browser to mobile viewport
        self.browser.set_window_size(375, 667)

        # Student visits login page on their phone
        login_page = LoginPage(self)
        login_page.navigate_to_login()

        # Submit button should have smaller padding on mobile (12px or less)
        submit_button = self.browser.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        padding = submit_button.value_of_css_property("padding")
        padding_px = int(padding.split()[0].replace("px", ""))

        self.assertLessEqual(
            padding_px,
            12,
            f"Button padding {padding_px}px is too large for mobile (should be ≤12px)",
        )
