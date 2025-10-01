from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from surveys.models import Question, Survey


def home_page(request):
    return render(request, "home.html")


def view_survey(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    return render(request, "survey.html", {"survey": mysurvey})


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
    return redirect(f"/surveys/{new_survey.id}/")


def add_question(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    Question.objects.create(text=request.POST["question_text"], survey=mysurvey)
    return redirect(f"/surveys/{mysurvey.id}/")
