from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

import csv
from io import BytesIO
import qrcode

from surveys.forms import QuestionForm
from surveys.models import Survey


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


# Display views
@login_required
def responses_list(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    # Check ownership
    if survey.owner != request.user:
        return HttpResponse("403 - Forbidden", status=403)

    # Group answers by question for easier display
    questions_with_answers = []
    for question in survey.question_set.all():
        answers = []
        for submission in survey.submissions.all():
            for answer in submission.answers.filter(question=question):
                answers.append(answer)
        questions_with_answers.append({"question": question, "answers": answers})

    context = {"survey": survey, "questions_with_answers": questions_with_answers}

    if request.headers.get("HX-Request"):
        return render(request, "partials/responses_list.html", context)
    return render(
        request,
        "dashboard.html",
        {"initial_view": "responses_list", **context},
    )


@login_required
def survey_detail(request, survey_id):
    survey_id = request.resolver_match.kwargs.get("survey_id")
    survey = get_object_or_404(Survey, id=survey_id)

    if survey.owner != request.user:
        return HttpResponse("403 - Forbidden", status=403)

    if request.method == "POST":
        # Get survey name if provided
        survey_name = request.POST.get("survey_name")

        # Check if this is a survey name update (no question text)
        if survey_name and not request.POST.get("text"):
            # Update survey name
            survey.name = survey_name
            survey.save()

            # For HTMX requests, return just the updated name container
            if request.headers.get("HX-Request"):
                # Return the display version (not edit form)
                return render(
                    request, "partials/survey_name_display.html", {"survey": survey}
                )

        # Handle adding a question (existing code)
        form = QuestionForm(for_survey=survey, data=request.POST)

        if form.is_valid():
            form.save()
            # Return updated question list for htmx
            if request.headers.get("HX-Request"):
                form = QuestionForm(for_survey=survey)  # Fresh form
                return render(
                    request,
                    "partials/question_list.html",
                    {"survey": survey, "form": form},
                )
            return redirect("instructors:survey_detail", survey_id=survey.id)
        else:
            # Return form with errors
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "partials/question_list.html",
                    {"survey": survey, "form": form},
                )
            # For non-htmx, show full page with errors
            return render(
                request,
                "dashboard.html",
                {"initial_view": "survey_detail", "survey": survey, "form": form},
            )

    # GET request - create fresh form
    form = QuestionForm(for_survey=survey)

    if request.headers.get("HX-Request"):
        # Check if we're in edit mode
        if request.GET.get("edit_mode") == "true":
            return render(request, "partials/survey_name_edit.html", {"survey": survey})
        return render(
            request, "partials/survey_editor.html", {"survey": survey, "form": form}
        )
    else:
        return render(
            request,
            "dashboard.html",
            {"initial_view": "survey_detail", "survey": survey, "form": form},
        )


@login_required
def surveys_list(request):
    if request.method == "GET":
        surveys = Survey.objects.filter(owner=request.user).order_by("-created_at")
        # If htmx request, return the survey list partial
        if request.headers.get("HX-Request"):
            return render(request, "partials/surveys_list.html", {"surveys": surveys})
        else:
            return render(
                request,
                "dashboard.html",
                {"initial_view": "surveys_list", "surveys": surveys},
            )


# Action views
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
                response["HX-Push-Url"] = reverse(
                    "instructors:survey_detail", args=[survey.id]
                )
                return response
            else:
                return redirect("instructors:survey_detail", survey_id=survey.id)

    # GET request - show the create form
    if request.headers.get("HX-Request"):
        return render(request, "partials/create_survey.html")
    else:
        return render(request, "dashboard.html", {"initial_view": "create_survey"})


@login_required
def export_responses(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    # Check ownership
    if survey.owner != request.user:
        return HttpResponse("403 - Forbidden", status=403)

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
            if answer:
                # Combine answer text with comment if present
                cell_content = answer.answer_text
                if answer.comment_text:
                    cell_content += f" | Comment: {answer.comment_text}"
                row.append(cell_content)
            else:
                row.append("")
        writer.writerow(row)

    return response


@login_required
def generate_qr_code(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)

    # Only survey owner can get the QR code
    if survey.owner != request.user:
        return HttpResponse("403 - Forbidden", status=403)

    # Generate the full URL for the survey
    survey_url = request.build_absolute_uri(
        reverse("students:take_survey", args=[survey_id])
    )

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
