from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from surveys.models import Survey


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


@login_required
def survey_list(request):
    if request.method == "GET":
        surveys = Survey.objects.filter(owner=request.user).order_by("-created_at")
        # If htmx request, return the survey list partial
        if request.headers.get("HX-Request"):
            return render(request, "partials/survey_list.html", {"surveys": surveys})
        else:
            return render(
                request,
                "dashboard.html",
                {"initial_view": "survey_list", "surveys": surveys},
            )


@login_required
def create_survey(request):
    if request.method == "POST":
        survey_name = request.POST.get("survey_name")
        if survey_name:
            # Create the survey
            survey = Survey.objects.create(owner=request.user, name=survey_name)
            # If htmx request, return the survey editor partial
            if request.headers.get("HX-Request"):
                response = render(
                    request, "partials/survey_editor.html", {"survey": survey}
                )
                response["HX-Push-Url"] = f"/instructor/surveys/{survey.id}/"
                return response
            else:
                return redirect(survey)  # Uses get_absolute_url() from Survey model

    # GET request - show the create form
    if request.headers.get("HX-Request"):
        return render(request, "partials/create_survey.html")
    else:
        return render(request, "dashboard.html", {"initial_view": "create_survey"})


@login_required
def survey_detail(request, survey_id):
    survey_id = request.resolver_match.kwargs.get("survey_id")
    survey = get_object_or_404(Survey, id=survey_id)

    if survey.owner != request.user:  # Check ownership
        return HttpResponseForbidden()  # Returns 403

    if request.headers.get("HX-Request"):
        return render(request, "partials/survey_editor.html", {"survey": survey})
    else:
        return render(
            request,
            "dashboard.html",
            {"initial_view": "survey_detail", "survey": survey},
        )


@login_required
def survey_responses(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.headers.get("HX-Request"):
        return render(request, "partials/survey_responses.html", {"survey": survey})
    return render(
        request,
        "dashboard.html",
        {"initial_view": "survey_responses", "survey": survey},
    )


@login_required
def analytics(request):
    return HttpResponse("Instructor analytics placeholder")
