from django.http import HttpResponse
from django.shortcuts import redirect, render
from surveys.models import Question


def home_page(request):
    return render(request, "home.html")


def view_question(request):
    questions = Question.objects.all()
    return render(request, "question.html", {"questions": questions})


def new_question(request):
    Question.objects.create(text=request.POST["question_text"])
    return redirect("/questions/the-only-question-in-the-world/")
