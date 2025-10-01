from django.urls import path

from surveys import views

urlpatterns = [
    path("new", views.new_survey, name="new_survey"),
    path("<int:survey_id>/", views.view_survey, name="view_survey"),
]
