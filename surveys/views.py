from django.http import HttpResponse
from django.shortcuts import redirect, render
from surveys.models import Question, Survey


def home_page(request):
    return render(request, "home.html")


def view_survey(request):
    questions = Question.objects.all()
    return render(request, "survey.html", {"questions": questions})


def new_survey(request):
    Question.objects.create(text=request.POST["question_text"])
    return redirect("/surveys/the-only-survey-in-the-world/")
