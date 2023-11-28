from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datetime import date

from .models import MonthlyPlan, TodayPlan


class MonthlyPlanSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.name")
    monthly_possible = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyPlan
        fields = (
            "pk",
            "owner",
            "monthly_income",
            "monthly_saving",
            "monthly_spending",
            "monthly_total_spending",
            "monthly_possible",
        )

    def get_monthly_possible(self, obj):
        return obj.monthly_income - obj.monthly_saving

    def validate(self, data):
        if data["monthly_income"] < data["monthly_saving"]:
            raise ValidationError("월 저축금액은 월 수입보다 클 수 없습니다.")
        return data


class TodayPlanSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.name")
    date = serializers.SerializerMethodField()
    today_possible = serializers.SerializerMethodField()

    class Meta:
        model = TodayPlan
        fields = (
            "pk",
            "owner",
            "date",
            "today_spending",
            "today_possible",
        )

    def get_date(self, obj):
        return date.today()
