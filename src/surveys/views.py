from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from io import BytesIO
import qrcode

from accounts.models import User
from surveys.forms import ExistingSurveyQuestionForm, QuestionForm, SurveyAnswerForm
from surveys.models import Answer, Survey


def home_page(request):
    return render(request, "home.html", {"form": QuestionForm()})


@login_required  # ensure only logged-in users can create new surveys
def new_survey(request):
    form = QuestionForm(data=request.POST)
    if form.is_valid():
        new_survey = Survey.objects.create()
        new_survey.owner = request.user  # set the owner to the logged-in user
        new_survey.save()
        form.save(for_survey=new_survey)
        return redirect(new_survey)  # uses get_absolute_url() method of Survey model
    else:
        return render(request, "home.html", {"form": form})


def view_survey(request, survey_id):
    mysurvey = Survey.objects.get(id=survey_id)
    form = ExistingSurveyQuestionForm(for_survey=mysurvey)

    if request.method == "POST":
        form = ExistingSurveyQuestionForm(for_survey=mysurvey, data=request.POST)
        if form.is_valid():
            form.save()

            # htmx automatically adds HX-Request header to every request it makes
            if request.headers.get("HX-Request"):
                # Create fresh form (so input box is cleared)
                form = ExistingSurveyQuestionForm(for_survey=mysurvey)
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

    return render(request, "survey.html", {"survey": mysurvey, "form": form})


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

    return render(request, "student_survey.html", {"survey": survey})


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
