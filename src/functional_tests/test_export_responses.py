from selenium.webdriver.common.by import By
from .base import FunctionalTest
from surveys.models import Answer, Question, Submission, Survey
from accounts.models import User


class ExportResponsesTest(FunctionalTest):
    def test_instructor_can_export_survey_responses_to_csv(self):
        # Aya creates a survey with responses
        # Create and login the instructor first
        self.login("instructor@test.com")

        # Then get the user and create the survey with custom questions
        instructor = User.objects.get(email="instructor@test.com")
        survey = Survey.objects.create(owner=instructor)
        q1 = Question.objects.create(
            survey=survey, text="Question 1", question_type="text"
        )
        q2 = Question.objects.create(
            survey=survey,
            text="Rate this",
            question_type="rating",
            options=[1, 2, 3, 4, 5],
        )

        # Some responses exist
        submission = Submission.objects.create(survey=survey)
        Answer.objects.create(
            question=q1, answer_text="Answer 1", submission=submission
        )
        Answer.objects.create(
            question=q2, answer_text="5", comment_text="Great!", submission=submission
        )

        # She goes to the survey detail page
        self.browser.get(f"{self.live_server_url}/instructor/surveys/{survey.id}/")

        # They see an "Export to CSV" button
        export_button = self.browser.find_element(By.LINK_TEXT, "Export to CSV")

        # They click it (can't easily test the actual download in Selenium,
        # but can verify the link exists and points to the right URL)
        export_url = export_button.get_attribute("href")
        self.assertIn(f"/instructor/surveys/{survey.id}/export/", export_url)
