from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from surveys.forms import QuestionForm
from surveys.models import Survey


def home_page(request):
    return render(request, "home.html", {"form": QuestionForm()})


def view_survey(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    form = QuestionForm()

    if request.method == "POST":
        form = QuestionForm(data=request.POST)
        if form.is_valid():
            form.save(for_survey=mysurvey)
            return redirect(mysurvey)  # uses get_absolute_url() method of Survey model

    return render(request, "survey.html", {"survey": mysurvey, "form": form})


def new_survey(request):
    form = QuestionForm(data=request.POST)
    if form.is_valid():
        new_survey = Survey.objects.create()
        form.save(for_survey=new_survey)
        return redirect(new_survey)  # uses get_absolute_url() method of Survey model
    else:
        return render(request, "home.html", {"form": form})
