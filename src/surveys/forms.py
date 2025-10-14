from django import forms
from django.core.exceptions import ValidationError

from surveys.models import Answer, Question, Survey

DUPLICATE_QUESTION_ERROR = "You've already got this question in your survey"
EMPTY_SURVEY_NAME_ERROR = "You can't have a survey without a name"
EMPTY_QUESTION_ERROR = "You can't have an empty question"


class QuestionForm(forms.Form):
    text = forms.CharField(
        error_messages={"required": EMPTY_QUESTION_ERROR},
        required=True,
    )

    def __init__(self, for_survey=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._for_survey = for_survey

    def clean_text(self):
        text = self.cleaned_data["text"]
        if (
            self._for_survey
            and self._for_survey.question_set.filter(text=text).exists()
        ):
            raise forms.ValidationError(DUPLICATE_QUESTION_ERROR)
        return text

    def save(self, for_survey=None):
        # Accept for_survey as parameter for backwards compatibility
        survey = for_survey or self._for_survey
        if not survey:
            raise ValueError("A survey must be provided either in __init__ or save()")

        return Question.objects.create(
            survey=survey,
            text=self.cleaned_data["text"],
        )


class SurveyAnswerForm(forms.Form):
    def __init__(self, survey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey = survey

        # Dynamically add a field for each question
        for question in survey.question_set.all():
            field_name = f"response_{question.id}"

            if question.question_type == "multiple_choice":
                choices = [(option, option) for option in question.options]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    required=False,
                    widget=forms.RadioSelect,
                    choices=choices,
                )
            elif question.question_type == "rating":
                choices = [(option, option) for option in question.options]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    required=False,
                    widget=forms.RadioSelect,
                    choices=choices,
                )

            elif question.question_type == "checkbox":
                choices = [(option, option) for option in question.options]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question.text,
                    required=False,
                    widget=forms.CheckboxSelectMultiple,
                    choices=choices,
                )
            elif question.question_type == "yes_no":
                choices = [(option, option) for option in question.options]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    required=False,
                    widget=forms.RadioSelect,
                    choices=choices,
                )

            else:  # text question
                self.fields[field_name] = forms.CharField(
                    label=question.text, required=False
                )

            # Add comment field for non-text question types
            if question.question_type != "text":
                comment_field_name = f"comment_{question.id}"
                self.fields[comment_field_name] = forms.CharField(
                    label="Additional comments (optional)",
                    required=False,
                    widget=forms.Textarea(attrs={"rows": 2}),
                )

    def save(self):
        from surveys.models import Submission

        # Create a submission for this set of answers
        submission = Submission.objects.create(survey=self.survey)

        for question in self.survey.question_set.all():
            field_name = f"response_{question.id}"
            comment_field_name = f"comment_{question.id}"

            answer_text = self.cleaned_data.get(field_name, "")
            comment_text = self.cleaned_data.get(comment_field_name, "")

            # Only save if there's either an answer or a comment
            if answer_text or comment_text:
                Answer.objects.create(
                    question=question,
                    answer_text=answer_text,
                    comment_text=comment_text,
                    submission=submission,
                )


class SurveyCreationForm(QuestionForm):
    survey_name = forms.CharField(
        error_messages={"required": EMPTY_SURVEY_NAME_ERROR},
        required=True,
    )

    def save(self):
        survey = Survey.objects.create(name=self.cleaned_data["survey_name"])
        super().save(for_survey=survey)
        return survey


class SurveyEditForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Survey name",
                    "id": "survey-name-input",
                    "required": True,
                }
            )
        }
        error_messages = {
            "name": {
                "required": "Survey name cannot be empty",
                "max_length": "Survey name is too long",
            }
        }
