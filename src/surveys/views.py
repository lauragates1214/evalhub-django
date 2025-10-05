from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from surveys.forms import ExistingSurveyQuestionForm, QuestionForm
from surveys.models import Survey


def home_page(request):
    return render(request, "home.html", {"form": QuestionForm()})


@login_required  # ensure only logged-in users can create new surveys
def new_survey(request):
    form = QuestionForm(data=request.POST)
    if form.is_valid():
        new_survey = Survey.objects.create()
        form.save(for_survey=new_survey)
        return redirect(new_survey)  # uses get_absolute_url() method of Survey model
    else:
        return render(request, "home.html", {"form": form})


def view_survey(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    form = ExistingSurveyQuestionForm(for_survey=mysurvey)

    if request.method == "POST":
        form = ExistingSurveyQuestionForm(for_survey=mysurvey, data=request.POST)
        if form.is_valid():
            form.save()

            # htmx automatically adds HX-Request header to every request it makes
            if request.headers.get("HX-Request"):
                # Create fresh form (so input box is cleared)
                form = ExistingSurveyQuestionForm(for_survey=mysurvey)
                # Return just the fragment, not full page
                return render(
                    request,
                    "partials/question_list.html",
                    {"survey": mysurvey, "form": form},
                )

            # Normal POST still works when no HX-Request header present; full page reload
            return redirect(mysurvey)  # uses get_absolute_url() method of Survey model
    return render(request, "survey.html", {"survey": mysurvey, "form": form})


def my_surveys(request, email):
    return render(request, "my_surveys.html")
