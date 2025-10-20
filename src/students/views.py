"""
AI Assistance Note:
This module was developed using AI tools (Claude, VS Code AI) for:
- Initial test case generation following TDD patterns
- Debugging and interpreting test failures
- Explaining Django/htmx concepts and patterns
All architecture and design decisions and final implementations are my own work.
"""

from django.shortcuts import get_object_or_404, render

from surveys.forms import (
    SurveyAnswerForm,
)
from surveys.models import Survey


def take_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "POST":
        form = SurveyAnswerForm(survey=survey, data=request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "partials/confirmation_message.html",
                    {"survey": survey, "submitted": True},
                )
            # Render confirmation instead of redirecting
            return render(
                request,
                "student_survey.html",
                {"survey": survey, "submitted": True},
            )
    else:
        form = SurveyAnswerForm(survey=survey)

    return render(request, "student_survey.html", {"survey": survey, "form": form})
