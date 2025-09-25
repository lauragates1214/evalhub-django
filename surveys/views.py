from django.http import HttpResponse
from django.shortcuts import redirect, render
from surveys.models import Question, Survey


def home_page(request):
    return render(request, "home.html")


def view_survey(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    return render(request, "survey.html", {"survey": mysurvey})


def new_survey(request):
    new_survey = Survey.objects.create()
    Question.objects.create(text=request.POST["question_text"], survey=new_survey)
    return redirect(f"/surveys/{new_survey.id}/")


def add_question(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    Question.objects.create(text=request.POST["question_text"], survey=mysurvey)
    return redirect(f"/surveys/{mysurvey.id}/")
