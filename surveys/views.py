from django.http import HttpResponse
from django.shortcuts import redirect, render
from surveys.models import Survey


def home_page(request):
    if request.method == "POST":
        Survey.objects.create(text=request.POST["survey_text"])
        return redirect("/")

    surveys = Survey.objects.all()
    return render(
        request,
        "home.html",
        {"surveys": surveys},
    )
