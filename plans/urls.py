from django.urls import path
from . import views


urlpatterns = [
    path("monthly/", views.MonthlyPlanView.as_view()),
    path("monthly/<str:owner>/", views.MonthlyPlanDetailView.as_view()),
    path("today/<str:owner>/", views.TodayPlanView.as_view()),
]
