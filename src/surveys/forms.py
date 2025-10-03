from django import forms
from django.core.exceptions import ValidationError

from surveys.models import Question

DUPLICATE_QUESTION_ERROR = "You've already got this question in your survey"
EMPTY_QUESTION_ERROR = "You can't have an empty question"


class QuestionForm(forms.Form):
    text = forms.CharField(
        error_messages={"required": EMPTY_QUESTION_ERROR},
        required=True,
    )

    # custom save method (override) to associate question with a survey
    def save(self, for_survey):
        return Question.objects.create(
            survey=for_survey,
            text=self.cleaned_data["text"],
        )


class ExistingSurveyQuestionForm(QuestionForm):
    def __init__(self, for_survey, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call parent constructor
        self._for_survey = for_survey

    # custom method for validation to prevent duplicate questions in the same survey
    def clean_text(self):
        text = self.cleaned_data["text"]
        if self._for_survey.question_set.filter(text=text).exists():
            raise forms.ValidationError(DUPLICATE_QUESTION_ERROR)
        return text

    # use parent class save method
    def save(self):
        return super().save(for_survey=self._for_survey)
