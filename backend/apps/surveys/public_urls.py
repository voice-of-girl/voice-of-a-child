from django.urls import path

from .public_views import PublicSurveySubmitView, PublicSurveyView

urlpatterns = [
    path(
        "<str:public_token>/",
        PublicSurveyView.as_view(),
        name="public-survey-detail",
    ),
    path(
        "<str:public_token>/responses/",
        PublicSurveySubmitView.as_view(),
        name="public-survey-submit",
    ),
]