from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datetime import date

from .models import MonthlyPlan, TodayPlan

from payments.models import Payment
# from payments.serializers import PaymentSerializer

class MonthlyPlanSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.name")
    monthly_possible = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyPlan
        fields = (
            # "pk",
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
        monthly_income = data.get("monthly_income")
        monthly_saving = data.get("monthly_saving")

        if monthly_income is not None and monthly_saving is not None:
            if monthly_income < monthly_saving:
                raise ValidationError("저축 금액이 수입 금액보다 많습니다.")
        return data

    def save(self):
        updated_income = "monthly_income" in self.validated_data
        updated_saving = "monthly_saving" in self.validated_data

        if updated_income or updated_saving:
            monthly_income = self.validated_data.get(
                "monthly_income", self.instance.monthly_income
            )
            monthly_saving = self.validated_data.get(
                "monthly_saving", self.instance.monthly_saving
            )
            self.validated_data["monthly_possible"] = monthly_income - monthly_saving
        return super().save()


class TodayPlanSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.name")
    date = serializers.DateField()
    today_possible = serializers.SerializerMethodField()
    # today_spending = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = TodayPlan
        fields = (
            # "pk",
            "owner",
            "date",
            "today_spending",
            "today_possible",
        )

    def get_date(self, obj):
        return date.today()

    def get_today_possible(self, obj):
        monthly_plan = MonthlyPlan.objects.get(owner=obj.owner)
        total_spent_this_month = 0

        payments_this_month = Payment.objects.filter(
            owner=obj.owner,
            pay_date__month=obj.date.month,
            pay_date__year=obj.date.year,
        )
        
        for payment in payments_this_month:
            total_spent_this_month += payment.pay_price

        today_possible = monthly_plan.monthly_possible - total_spent_this_month
        today_possible = max(today_possible, 0)
        return today_possible