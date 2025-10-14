from django.urls import path

from surveys import views

app_name = "surveys"  # Namespace for survey URLs

urlpatterns = [
    path("new", views.new_survey, name="new_survey"),
    path("<int:survey_id>/", views.view_survey, name="view_survey"),
    path("users/<str:email>/", views.my_surveys, name="my_surveys"),
    path("<int:survey_id>/qr/", views.survey_qr_code, name="survey_qr_code"),
    path(
        "<int:survey_id>/responses/",
        views.dashboard_survey_responses,
        name="dashboard_survey_responses",
    ),
]
