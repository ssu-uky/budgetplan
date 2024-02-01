from django.contrib import admin
from .models import MonthlyPlan, TodayPlan


@admin.register(MonthlyPlan)
class MonthlyPlanAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "owner",
        "monthly_income",
        "monthly_saving",
        "monthly_total_spending",
        "monthly_possible",
    )
    list_display_links = ("pk", "owner")


@admin.register(TodayPlan)
class TodayPlanAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "owner",
        "today_total_spending",
        "today_possible",
        "date",
    )
    list_display_links = ("pk", "owner")
