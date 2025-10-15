from django.urls import path
from . import views

app_name = "students"  # Namespace for student URLs


urlpatterns = [
    path("survey/<int:survey_id>/", views.survey, name="take_survey"),
]
