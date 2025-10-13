from django.shortcuts import get_object_or_404, render

from surveys.forms import (
    SurveyAnswerForm,
)
from surveys.models import Survey


def survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "POST":
        form = SurveyAnswerForm(survey=survey, data=request.POST)
        if form.is_valid():
            form.save()
            # Render confirmation instead of redirecting
            return render(
                request, "student_survey.html", {"survey": survey, "submitted": True}
            )
    else:
        form = SurveyAnswerForm(survey=survey)

    return render(request, "student_survey.html", {"survey": survey, "form": form})
