from selenium.webdriver.common.by import By
from .base import FunctionalTest
from surveys.models import Survey, Question, Answer
from accounts.models import User


class ViewResponsesTest(FunctionalTest):
    def test_instructor_can_view_responses_to_their_survey(self):
        # Instructor creates a survey with questions
        self.login("instructor@test.com")
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        q1 = Question.objects.create(survey=survey, text="How was the session?")
        q2 = Question.objects.create(survey=survey, text="Any suggestions?")

        # Some students have submitted responses
        Answer.objects.create(question=q1, answer_text="It was great!")
        Answer.objects.create(question=q1, answer_text="Very informative")
        Answer.objects.create(question=q2, answer_text="More capybaras please")

        # Instructor visits their survey page
        self.browser.get(f"{self.live_server_url}/surveys/{survey.id}/")

        # They see a link to view responses
        responses_link = self.browser.find_element(By.LINK_TEXT, "View Responses")
        responses_link.click()

        # They're taken to a responses page
        self.assertIn("/surveys/", self.browser.current_url)
        self.assertIn("/responses/", self.browser.current_url)

        # They see all the responses grouped by question
        self.assertIn("How was the session?", self.browser.page_source)
        self.assertIn("It was great!", self.browser.page_source)
        self.assertIn("Very informative", self.browser.page_source)

        self.assertIn("Any suggestions?", self.browser.page_source)
        self.assertIn("More capybaras please", self.browser.page_source)
