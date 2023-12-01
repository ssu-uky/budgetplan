from django.urls import path
from . import views


urlpatterns = [
    path("new/", views.NewPaymentView.as_view(), name="create_payment"),
    path(
        "<str:owner>/<int:year>-<int:month>/",
        views.PaymentMonthlyListView.as_view(),
        name="monthly_payment",
    ),
    path(
        "<str:owner>/<int:year>-<int:month>-<int:day>/",
        views.PaymentDailyListView.as_view(),
        name="daily_payment",
    ),
    path("<int:pk>/", views.PaymentDetailView.as_view(), name="detail_payment"),
]
