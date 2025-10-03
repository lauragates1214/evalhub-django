from django import forms

from surveys.models import Question

EMPTY_QUESTION_ERROR = "You can't have an empty question"


class QuestionForm(forms.models.ModelForm):
    class Meta:  # Specifies which model the form is for and which fields to include
        model = Question
        fields = ("text",)
        widgets = {
            "text": forms.widgets.TextInput(
                attrs={
                    "placeholder": "Enter a question",
                    "class": "form-control form-control-lg",
                }
            ),
        }
        error_messages = {"text": {"required": EMPTY_QUESTION_ERROR}}

    def save(self, for_survey):
        self.instance.survey = for_survey  # .instance attribute represents db objec that is being modified or created
        return super().save()
