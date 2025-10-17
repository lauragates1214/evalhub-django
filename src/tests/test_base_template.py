import os
from django.test import TestCase
from django.template.loader import get_template
from django.conf import settings


class BaseTemplateInheritanceTest(TestCase):
    def test_project_level_base_template_exists(self):
        template_path = os.path.join(settings.BASE_DIR.parent, "templates", "base.html")
        self.assertTrue(
            os.path.exists(template_path),
            f"Project-level base.html should exist at {template_path}",
        )

    def test_instructors_app_has_no_base_template(self):
        template_path = os.path.join(
            settings.BASE_DIR.parent, "instructors", "templates", "base.html"
        )
        self.assertFalse(
            os.path.exists(template_path),
            "instructors/templates/base.html should not exist",
        )

    def test_students_app_has_no_base_template(self):
        template_path = os.path.join(
            settings.BASE_DIR.parent, "students", "templates", "base.html"
        )
        self.assertFalse(
            os.path.exists(template_path),
            "students/templates/base.html should not exist",
        )

    def test_project_base_template_has_navbar(self):
        template = get_template("base.html")
        template_source = template.template.source
        self.assertIn("navbar", template_source)
        self.assertIn("EvalHub", template_source)

    def test_accounts_login_extends_project_base(self):
        template = get_template("registration/login.html")
        template_source = template.template.source
        self.assertIn("{% extends", template_source)
        self.assertIn("'base.html'", template_source)

    def test_instructor_dashboard_extends_project_base(self):
        template = get_template("dashboard.html")
        template_source = template.template.source
        self.assertIn("{% extends", template_source)
        self.assertIn('"base.html"', template_source)
