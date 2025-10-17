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

    def test_text_inputs_have_16px_border_radius(self):
        css_path = finders.find("CACHE/css/output.a9ceb1e24868.css")
        if css_path is None:
            cache_dir = Path(__file__).parent.parent / "CACHE" / "css"
            css_files = list(cache_dir.glob("*.css"))
            self.assertTrue(len(css_files) > 0, "No compressed CSS files found")
            css_path = str(css_files[0])

        with open(css_path, "r") as f:
            css_content = f.read()

        self.assertIn("border-radius", css_content)
        # Check for input[type=text] with 16px border-radius (quotes optional in compiled CSS)
        self.assertTrue(
            re.search(
                r'input\[type=["\']?text["\']?\][^}]*border-radius[^}]*16px',
                css_content,
                re.DOTALL,
            ),
            "Text inputs should have 16px border-radius in compiled CSS",
        )


class TypographyTest(TestCase):
    def test_h1_uses_roboto_slab_font(self):
        """H1 headers should use Roboto Slab font family"""
        css_path = finders.find("CACHE/css/output.65a4b43f4b54.css")
        if css_path is None:
            cache_dir = Path(__file__).parent.parent / "CACHE" / "css"
            css_files = list(cache_dir.glob("*.css"))
            self.assertTrue(len(css_files) > 0, "No compressed CSS files found")
            css_path = str(css_files[0])

        with open(css_path, "r") as f:
            css_content = f.read()

        # Check for h1 with Roboto Slab font
        self.assertTrue(
            re.search(
                r"h1[^}]*font-family[^}]*Roboto Slab",
                css_content,
                re.DOTALL,
            ),
            "H1 should use Roboto Slab font family in compiled CSS",
        )


class ColorStylingTest(TestCase):
    def test_navbar_brand_has_primary_color(self):
        """Navbar brand should use primary forest green color"""
        css_path = finders.find("CACHE/css/output.db4c10713910.css")
        if css_path is None:
            cache_dir = Path(__file__).parent.parent / "CACHE" / "css"
            css_files = list(cache_dir.glob("*.css"))
            self.assertTrue(len(css_files) > 0, "No compressed CSS files found")
            css_path = str(css_files[0])

        with open(css_path, "r") as f:
            css_content = f.read()

        # Check for navbar-brand with primary color
        self.assertTrue(
            re.search(
                r"\.navbar-brand[^}]*color[^}]*#2D5A27",
                css_content,
                re.DOTALL,
            ),
            "Navbar brand should use primary color (#2D5A27) in compiled CSS",
        )
