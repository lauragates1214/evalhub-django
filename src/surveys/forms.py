from django import forms
from django.core.exceptions import ValidationError

from surveys.models import Question

DUPLICATE_QUESTION_ERROR = "You've already got this question in your survey"
EMPTY_QUESTION_ERROR = "You can't have an empty question"


class QuestionForm(forms.models.ModelForm):
    class Meta:  # Specifies which model the form is for and which fields to include
        model = Question
        fields = ("text",)
        widgets = {
            "text": forms.widgets.TextInput(
                attrs={
                    "placeholder": "Enter a survey question",
                    "class": "form-control form-control-lg",
                }
            ),
        }
        error_messages = {"text": {"required": EMPTY_QUESTION_ERROR}}

    # custom method for validation(override) to add bootstrap is-invalid CSS class to invalid fields
    def is_valid(self):
        result = super().is_valid()
        if not result:
            self.fields["text"].widget.attrs["class"] += " is-invalid"
        return result  # return True/False if form is valid

    # custom save method (override) to associate question with a survey
    def save(self, for_survey):
        self.instance.survey = for_survey  # .instance attribute represents db objec that is being modified or created
        return super().save()


class ExistingSurveyQuestionForm(QuestionForm):
    def __init__(self, for_survey, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call parent constructor
        self.instance.survey = for_survey  # associate question with survey instance

    # custom method for validation to prevent duplicate questions in the same survey
    def clean_text(self):
        text = self.cleaned_data["text"]
        if self.instance.survey.question_set.filter(text=text).exists():
            raise forms.ValidationError(DUPLICATE_QUESTION_ERROR)
        return text

    # use parent class save method
    def save(self):
        return forms.models.ModelForm.save(self)
