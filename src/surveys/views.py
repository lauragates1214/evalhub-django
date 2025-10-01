from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from surveys.models import Question, Survey


def home_page(request):
    return render(request, "home.html")


def view_survey(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    error = None

    if request.method == "POST":
        try:
            question = Question(text=request.POST["question_text"], survey=mysurvey)
            question.full_clean()
            question.save()
            return redirect(mysurvey)  # uses get_absolute_url() method of Survey model
        except ValidationError:
            error = "You can't have an empty question"

    return render(request, "survey.html", {"survey": mysurvey, "error": error})


def new_survey(request):
    new_survey = Survey.objects.create()
    question = Question.objects.create(
        text=request.POST["question_text"], survey=new_survey
    )
    try:
        question.full_clean()
        question.save()
    except ValidationError:
        new_survey.delete()
        error = "You can't have an empty question"
        return render(request, "home.html", {"error": error})
    return redirect(new_survey)  # uses get_absolute_url() method of Survey model
