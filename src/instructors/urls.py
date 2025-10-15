from django.urls import path
from . import views

app_name = "instructors"  # Namespace for instructor URLs

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Display URLs
    path(
        "surveys/<int:survey_id>/responses/",
        views.responses_list,
        name="responses_list",
    ),
    path(
        "surveys/<int:survey_id>/",
        views.survey_detail,
        name="survey_detail",
    ),
    path("surveys/", views.surveys_list, name="surveys_list"),
    # Action URLs
    path(
        "surveys/create/",
        views.create_survey,
        name="create_survey",
    ),
    path(
        "surveys/<int:survey_id>/export/",
        views.export_responses,
        name="export_responses",
    ),
    path(
        "surveys/<int:survey_id>/qr/",
        views.generate_qr_code,
        name="generate_qr_code",
    ),
]
