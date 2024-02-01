from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from datetime import date

from .models import Payment

from plans.models import MonthlyPlan, TodayPlan


class PaymentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.name")

    class Meta:
        model = Payment
        fields = (
            "pk",
            "owner",
            "pay_type",
            "pay_title",
            "pay_content",
            "pay_price",
            "pay_date",
        )
        read_only_fields = (
            "pk",
            "owner",
        )

    def validate_pay_date(self, value):
        """
        지출 날짜가 오늘 날짜보다 미래인 경우 ValidationError 발생
        """
        if value > date.today():
            raise ValidationError("지출 날짜는 오늘 날짜보다 미래일 수 없습니다.")
        return value

      
class MonthlyPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("pay_title", "pay_price")
