from selenium.webdriver.common.by import By

from .base import FunctionalTest


class CommonBaseTemplateTest(FunctionalTest):
    """Functional test to verify all pages share a common base template with consistent branding."""

    def test_evalhub_branding_appears_on_all_pages(self):
        """EvalHub branding appears consistently across login, instructor and student pages."""

        # Persephone visits the login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")

        # They see the EvalHub brand in the navbar
        navbar = self.browser.find_element(By.CSS_SELECTOR, "nav.navbar")
        self.assertTrue(navbar.is_displayed())
        brand = self.browser.find_element(By.CLASS_NAME, "navbar-brand")
        self.assertEqual(brand.text, "EvalHub")
        self.assertTrue(brand.is_displayed())

        # They log in using helper method
        email = "persephone@test.com"
        self.login(email)

        # On the instructor dashboard, they still see EvalHub branding
        navbar = self.browser.find_element(By.CSS_SELECTOR, "nav.navbar")
        self.assertTrue(navbar.is_displayed())
        brand = self.browser.find_element(By.CLASS_NAME, "navbar-brand")
        self.assertEqual(brand.text, "EvalHub")
        self.assertTrue(brand.is_displayed())

        # They create a survey to test student pages
        survey = self.create_survey_with_questions(
            email, ["Behold the majestic capybara?"]
        )
        self.logout()

        # A student visits a survey page
        self.browser.get(f"{self.live_server_url}/student/survey/{survey.id}/")

        # They also see the EvalHub branding in the navbar
        navbar = self.browser.find_element(By.CSS_SELECTOR, "nav.navbar")
        self.assertTrue(navbar.is_displayed())
        brand = self.browser.find_element(By.CLASS_NAME, "navbar-brand")
        self.assertEqual(brand.text, "EvalHub")
        self.assertTrue(brand.is_displayed())
