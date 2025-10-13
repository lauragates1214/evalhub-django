"""
URL configuration for evalhub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from surveys import views as survey_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("instructor/", include("instructors.urls")),
    path("student/", include("students.urls")),
    # TODO: Remove the below urls - deprecated
    path("", survey_views.home_page, name="home"),
    path("dashboard/", survey_views.dashboard_view, name="dashboard"),
    path(
        "dashboard/surveys/",
        survey_views.dashboard_my_surveys,
        name="dashboard_my_surveys",
    ),
    path(
        "dashboard/surveys/new/",
        survey_views.dashboard_create_survey,
        name="dashboard_create_survey",
    ),
    path(
        "dashboard/surveys/<int:survey_id>/",
        survey_views.dashboard_survey_detail,
        name="dashboard_survey_detail",
    ),
    path("surveys/", include("surveys.urls")),
    path(
        "survey/<int:survey_id>/",
        survey_views.student_survey_view,
        name="student_survey",
    ),
    path(
        "dashboard/surveys/<int:survey_id>/responses/",
        survey_views.dashboard_survey_responses,
        name="dashboard_survey_responses",
    ),
]
