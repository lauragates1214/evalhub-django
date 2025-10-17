from django.test import TestCase


class ResponsiveCSSTest(TestCase):
    def test_forms_scss_contains_mobile_media_query(self):
        forms_scss_path = "src/static/scss/_forms.scss"

        with open(forms_scss_path, "r") as f:
            content = f.read()

        self.assertIn("@media", content)
        self.assertIn("max-width", content)
        self.assertIn("border:", content.split("@media")[1])

    def test_buttons_scss_contains_mobile_media_query(self):
        buttons_scss_path = "src/static/scss/_buttons.scss"

        with open(buttons_scss_path, "r") as f:
            content = f.read()

        self.assertIn("@media", content)
        self.assertIn("max-width", content)
        self.assertIn("padding:", content.split("@media")[1])
