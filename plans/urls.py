from django.urls import path
from . import views


urlpatterns = [
    path("monthly/", views.MonthlyPlanView.as_view()),
    path("monthly/<str:owner>/", views.MonthlyPlanDetailView.as_view()),
    path("today/<str:owner>/", views.TodayView.as_view()),
    path(
        "<str:owner>/<int:year>-<int:month>-<int:day>/", views.TodayPlanView.as_view()
    ),
]
