from django import forms
from django.core.exceptions import ValidationError

from surveys.models import Answer, Question

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
