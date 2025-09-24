from django.test import TestCase
from django.http import HttpRequest
from surveys.views import home_page


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_renders_input_form(self):
        response = self.client.get("/")
        self.assertContains(response, '<form method="POST">')
        self.assertContains(response, '<input name="survey_text"')

    def test_can_save_a_POST_request(self):
        response = self.client.post("/", data={"survey_text": "A new survey"})
        self.assertContains(response, "A new survey")
        self.assertTemplateUsed(response, "home.html")

    def foo(x, y):
        return {"a": 1, "b": 2}

    def bar(x, y):
        return {"a": 1, "b": 4}
