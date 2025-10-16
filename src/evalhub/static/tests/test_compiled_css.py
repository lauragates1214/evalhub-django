from django.test import TestCase
from django.contrib.staticfiles import finders
import re
from pathlib import Path


class CompiledCSSTest(TestCase):
    def test_custom_css_exists(self):
        result = finders.find("CACHE/css/output.a9ceb1e24868.css")
        self.assertIsNotNone(result, "Compressed CSS not found in static files")

    def test_submit_buttons_have_16px_border_radius(self):
        css_path = finders.find("CACHE/css/output.a9ceb1e24868.css")
        if css_path is None:
            # Fallback: find any CSS file in CACHE
            cache_dir = Path(__file__).parent.parent / "CACHE" / "css"
            css_files = list(cache_dir.glob("*.css"))
            self.assertTrue(len(css_files) > 0, "No compressed CSS files found")
            css_path = str(css_files[0])

        with open(css_path, "r") as f:
            css_content = f.read()

        self.assertIn("border-radius", css_content)
        self.assertTrue(
            re.search(
                r'button\[type=["\']?submit["\']?\][^}]*border-radius:\s*16px',
                css_content,
                re.DOTALL,
            )
            or re.search(
                r"\.submit-btn[^}]*border-radius:\s*16px", css_content, re.DOTALL
            ),
            "Submit buttons should have 16px border-radius in compiled CSS",
        )
