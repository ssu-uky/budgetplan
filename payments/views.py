from django.shortcuts import get_object_or_404
from django.utils import timezone
import datetime

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError

from .models import Payment
from .serializers import PaymentSerializer

from plans.models import MonthlyPlan, TodayPlan
from users.models import User


class NewPaymentView(APIView):
    """
    POST : 지출 내역 입력
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "message": "지출 내역을 입력해주세요.",
                "pay_type": "지출 유형",
                "pay_title": "지출 제목",
                "pay_content": "지출 내용",
                "pay_price": "지출 금액",
                "pay_date": "지출 날짜",
            }
        )

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                {
                    "payment_pk": serializer.data["pk"],
                    "owner": serializer.data["owner"],
                    "message": "지출 내역이 저장되었습니다.",
                    "지출 유형": serializer.data["pay_type"],
                    "지출 제목": serializer.data["pay_title"],
                    "지출 내용": serializer.data["pay_content"],
                    "지출 금액": serializer.data["pay_price"],
                    "지출 날짜": serializer.data["pay_date"],
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentMonthlyListView(APIView):
    """
    GET : 한 달 지출 내역 조회 (yyyy-mm 입력)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, owner, year, month):
        if request.user.username != owner:
            raise PermissionDenied("접근 권한이 없습니다.")

        user = get_object_or_404(User, username=owner)
        payments = Payment.objects.filter(
            owner=user, pay_date__year=year, pay_date__month=month
        )

        total_pay_price = sum(payment.pay_price for payment in payments)

        serializer = PaymentSerializer(payments, many=True)

        return Response(
            {
                "이번 달 총 지출 금액": total_pay_price,
                "지출 내역": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class PaymentDailyListView(APIView):
    """
    GET : 하루 지출 내역 조회 (yyyy-mm-dd 입력)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, owner, year, month, day):
        if request.user.username != owner:
            raise PermissionDenied("접근 권한이 없습니다.")

        user = get_object_or_404(User, username=owner)
        payments = Payment.objects.filter(
            owner=user, pay_date__year=year, pay_date__month=month, pay_date__day=day
        )

        total_pay_price = sum(payment.pay_price for payment in payments)

        serializer = PaymentSerializer(payments, many=True)

        return Response(
            {
                "오늘 총 지출 금액": total_pay_price,
                "지출 내역": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class PaymentDetailView(APIView):
    """
    GET : 지출 내역 상세 조회
    PUT : 지출 내역 수정
    DELETE : 지출 내역 삭제
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)

        if payment.owner != request.user:
            raise PermissionDenied("본인만 접근 가능합니다.")

        return payment

    def get(self, request, pk):
        payment = self.get_object(request, pk)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def put(self, request, pk):
        payment = self.get_object(request, pk)
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "payment_pk": serializer.data["pk"],
                    "owner": serializer.data["owner"],
                    "message": "지출 내역이 수정되었습니다.",
                    "지출 유형": serializer.data["pay_type"],
                    "지출 제목": serializer.data["pay_title"],
                    "지출 내용": serializer.data["pay_content"],
                    "지출 금액": serializer.data["pay_price"],
                    "지출 날짜": serializer.data["pay_date"],
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payment = self.get_object(request, pk)
        payment.delete()
        return Response(
            {"message": "지출 내역이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )
