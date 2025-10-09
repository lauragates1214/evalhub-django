from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

import csv
from io import BytesIO
import qrcode

from accounts.models import User
from surveys.forms import (
    QuestionForm,
    SurveyAnswerForm,
    SurveyCreationForm,
)
from surveys.models import Survey


def home_page(request):
    return render(request, "home.html", {"form": SurveyCreationForm()})


@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")


@login_required
def dashboard_create_survey(request):
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
                response["HX-Push-Url"] = f"/dashboard/surveys/{survey.id}/"
                return response
            else:
                return redirect(f"/surveys/{survey.id}/")

    # GET request - show the create form
    if request.headers.get("HX-Request"):
        return render(request, "partials/create_survey.html")
    else:
        return render(request, "dashboard.html", {"initial_view": "create_survey"})


@login_required
def dashboard_survey_detail(request, survey_id):
    survey_id = request.resolver_match.kwargs.get("survey_id")
    survey = get_object_or_404(Survey, id=survey_id, owner=request.user)
    if request.headers.get("HX-Request"):
        return render(request, "partials/survey_editor.html", {"survey": survey})
    else:
        return render(
            request,
            "dashboard.html",
            {"initial_view": "survey_detail", "survey": survey},
        )


@login_required
def dashboard_my_surveys(request):
    if request.method == "GET":
        surveys = Survey.objects.filter(owner=request.user).order_by("-created_at")
        # If htmx request, return the survey list partial
        if request.headers.get("HX-Request"):
            return render(request, "partials/survey_list.html", {"surveys": surveys})
        else:
            return render(request, "dashboard.html", {"initial_view": "my_surveys"})


@login_required  # ensure only logged-in users can create new surveys
def new_survey(request):
    form = SurveyCreationForm(data=request.POST)
    if form.is_valid():
        new_survey = form.save()
        new_survey.owner = request.user  # set the owner to the logged-in user
        new_survey.save()
        return redirect(new_survey)  # uses get_absolute_url() method of Survey model
    else:
        return render(request, "home.html", {"form": form})


def view_survey(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    form = QuestionForm(for_survey=mysurvey)

    if request.method == "POST":
        form = QuestionForm(for_survey=mysurvey, data=request.POST)
        if form.is_valid():
            form.save()

            # htmx automatically adds HX-Request header to every request it makes
            if request.headers.get("HX-Request"):
                # Create fresh form (so input box is cleared)
                form = QuestionForm(for_survey=mysurvey)
                # Return just the fragment, not full page
                return render(
                    request,
                    "partials/question_list.html",
                    {"survey": mysurvey, "form": form},
                )

            # Normal POST still works when no HX-Request header present; full page reload
            return redirect(mysurvey)

        # Form is invalid - check if it's an htmx request
        if request.headers.get("HX-Request"):
            return render(
                request,
                "partials/question_list.html",
                {"survey": mysurvey, "form": form},
            )

    return render(request, "instructor_survey.html", {"survey": mysurvey, "form": form})


def my_surveys(request, email):
    owner = User.objects.get(email=email)
    return render(request, "my_surveys.html", {"owner": owner})


def student_survey_view(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    if request.method == "POST":
        form = SurveyAnswerForm(survey=survey, data=request.POST)
        if form.is_valid():
            form.save()
            # Render confirmation instead of redirecting
            return render(
                request, "student_survey.html", {"survey": survey, "submitted": True}
            )
    else:
        form = SurveyAnswerForm(survey=survey)

    return render(request, "student_survey.html", {"survey": survey, "form": form})


def survey_qr_code(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    # Generate the full URL for the survey
    survey_url = request.build_absolute_uri(survey.get_qr_code_url())

    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(survey_url)
    qr.make(fit=True)

    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")


def survey_responses(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    return render(request, "survey_responses.html", {"survey": survey})


def export_responses(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="survey_{survey_id}_responses.csv"'
    )

    writer = csv.writer(response)

    # Write header row with submission ID and question texts
    questions = survey.question_set.all()
    header = ["Submission ID"] + [q.text for q in questions]
    writer.writerow(header)

    # Write data rows - one row per submission
    for submission in survey.submissions.all():
        row = [submission.id]
        for question in questions:
            # Find the answer for this question in this submission
            answer = submission.answers.filter(question=question).first()
            row.append(answer.answer_text if answer else "")
        writer.writerow(row)

    return response
