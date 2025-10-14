from django.urls import path
from . import views

app_name = "instructors"  # Namespace for instructor URLs

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("surveys/", views.survey_list, name="survey_list"),
    path(
        "surveys/create/",
        views.create_survey,
        name="create_survey",
    ),
    path(
        "surveys/<int:survey_id>/",
        views.survey_detail,
        name="survey_detail",
    ),
    path(
        "surveys/<int:survey_id>/responses/",
        views.survey_responses,
        name="survey_responses",
    ),
    path(
        "surveys/<int:survey_id>/export/",
        views.export_responses,
        name="export_responses",
    ),
    path(
        "analytics/",
        views.analytics,
        name="analytics",
    ),
]
