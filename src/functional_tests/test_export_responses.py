from selenium.webdriver.common.by import By
from .base import FunctionalTest
from surveys.models import Answer, Question, Submission, Survey
from accounts.models import User


class ExportResponsesTest(FunctionalTest):
    """Tests for exporting survey responses to CSV"""

    def test_instructor_can_export_responses_list_to_csv(self):
        """Instructor with survey responses sees an Export to CSV button that links to the correct export endpoint."""

        # Aya creates a survey with responses
        self.login("instructor@test.com")

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
        self.browser.get(f"{self.live_server_url}/instructor/survey/{survey.id}/")

        # She sees an "Export to CSV" button
        export_button = self.browser.find_element(By.LINK_TEXT, "Export to CSV")

        # She verifies the link points to the right URL
        # (can't easily test the actual download in Selenium)
        export_url = export_button.get_attribute("href")
        self.assertIn(f"/instructor/survey/{survey.id}/export/", export_url)
