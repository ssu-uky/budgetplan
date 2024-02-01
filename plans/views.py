import calendar
from django.db.models import Sum

from django.utils import timezone
from datetime import datetime
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError

from .models import MonthlyPlan, TodayPlan
from .serializers import MonthlyPlanSerializer, TodayPlanSerializer

from payments.serializers import PaymentSerializer, MonthlyPaymentSerializer

from payments.models import Payment
from users.models import User


class MonthlyPlanView(APIView):
    """
    POST : 한 달 예산 계획 입력
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "message": "예산 계획을 입력해주세요.",
                "monthly_income": "한달 수입 금액",
                "monthly_saving": "한달 저축 금액",
            }
        )

    def post(self, request):
        exist_plan = MonthlyPlan.objects.filter(owner=request.user).exists()
        if exist_plan:
            return Response(
                {"message": "이미 예산 계획이 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = MonthlyPlanSerializer(data=request.data)
        if serializer.is_valid():
            monthly_income = serializer.validated_data.get("monthly_income")
            monthly_saving = serializer.validated_data.get("monthly_saving")
            monthly_possible = monthly_income - monthly_saving

            monthly_plan = MonthlyPlan(
                owner=request.user,
                monthly_income=monthly_income,
                monthly_saving=monthly_saving,
                monthly_possible=monthly_possible,
            )
            monthly_plan.save()

            return Response(
                {
                    "message": "예산 계획이 저장되었습니다.",
                    "한달 수입 금액": monthly_plan.monthly_income,
                    "한달 저축 금액": monthly_plan.monthly_saving,
                    "한달 사용 가능 금액": monthly_plan.monthly_possible,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MonthlyPlanDetailView(APIView):
    """
    GET : 한 달 예산 계획 조회
    PUT : 한 달 예산 계획 수정
    DELETE : 한 달 예산 계획 삭제
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, username):
        user = get_object_or_404(User, username=username)

        if user != request.user:
            raise PermissionDenied("접근 권한이 없습니다.")

        return get_object_or_404(MonthlyPlan, owner=user)

    def get(self, request, owner):
        monthly_plan = self.get_object(request, owner)

        today = timezone.localtime().date()
        current_year = today.year
        current_month = today.month

        month_total_spending = (
            Payment.objects.filter(
                owner=request.user,
                pay_date__year=current_year,
                pay_date__month=current_month,
            ).aggregate(total=Sum("pay_price"))["total"]
            or 0
        )

        serializer = MonthlyPlanSerializer(monthly_plan)
        data = serializer.data
        data["monthly_total_spending"] = month_total_spending

        current_monthly_possible = (
            monthly_plan.monthly_income
            - monthly_plan.monthly_saving
            - month_total_spending
        )

        # current_monthly_possible = max(current_monthly_possible, 0)  # 음수가 되지 않도록 합니다.
        current_monthly_possible = round(current_monthly_possible / 100) * 100
        data["monthly_possible"] = current_monthly_possible

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, owner):
        monthly_plan = self.get_object(request, owner)
        serializer = MonthlyPlanSerializer(
            monthly_plan, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()

            monthly_plan.refresh_from_db()

            return Response(
                {
                    "message": "예산 계획이 수정되었습니다.",
                    "한달 수입 금액": monthly_plan.monthly_income,
                    "한달 저축 금액": monthly_plan.monthly_saving,
                    "한달 사용 가능 금액": monthly_plan.monthly_possible,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, owner):
        monthly_plan = self.get_object(request, owner)
        monthly_plan.delete()

        return Response(
            {"message": "예산 계획이 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


class TodayPlanView(APIView):
    """
    GET : 오늘 사용 내역 및 사용 가능 금액 조회
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, owner, year, month, day):
        user = get_object_or_404(User, username=owner)

        if user != request.user:
            raise PermissionDenied("접근 권한이 없습니다.")

        try:
            url_date = datetime(year, month, day).date()
        except ValueError:
            return Response(
                {"message": "해당 일을 조회할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 지정된 날짜의 지출 내역 구하기
        payments = Payment.objects.filter(owner=user, pay_date=url_date)
        total_pay_price = sum(payment.pay_price for payment in payments)

        # 이번 달 예산 조회
        monthly_plan = MonthlyPlan.objects.filter(owner=user).first()
        if not monthly_plan:
            return Response(
                {"message": "이번 달 예산 계획이 설정되지 않았습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        else:
            monthly_possible = monthly_plan.monthly_possible

        # 해당 월의 총 일수와 현재 날짜 구하기
        _, last_day = calendar.monthrange(url_date.year, url_date.month)
        remaining_days = last_day - url_date.day + 1

        present_payments = (
            Payment.objects.filter(
                owner=user,
                pay_date__year=url_date.year,
                pay_date__month=url_date.month,
                pay_date__lte=url_date,
            ).aggregate(Sum("pay_price"))["pay_price__sum"]
            or 0
        )

        # 남은 일수에 따른 하루 사용 가능 금액 계산
        today_possible = (monthly_possible - present_payments) / remaining_days
        today_possible = round(today_possible / 100) * 100

        possible_present = monthly_possible - present_payments

        if possible_present >= 0:
            today_possible = possible_present / remaining_days
        else:
            today_possible = 0

        today_possible = round(today_possible / 100) * 100

        today_present = today_possible - total_pay_price

        return Response(
            {
                "today_date (날짜)": url_date,
                "monthly_possible (이번 달 사용 가능 한 금액)": monthly_possible,
                "present_payments (이번 달 현재까지의 사용금액)": present_payments,
                "possible_present (이번 달 사용 가능 한 금액)": possible_present,
                "today_possible (오늘 사용 가능 한 금액)": today_possible,
                "today_present (오늘 사용 가능 한 남은 금액)": today_present,
                "today_total_spending (오늘 총 지출 금액)": total_pay_price,
                "today_payments (사용 내역)": PaymentSerializer(payments, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
