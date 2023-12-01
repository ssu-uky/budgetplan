import calendar
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError

from .models import MonthlyPlan, TodayPlan
from .serializers import MonthlyPlanSerializer, TodayPlanSerializer

from payments.models import Payment
from users.models import User


class MonthlyPlanView(APIView):
    """
    POST : 한 달 예산 계획 입력
    PUT : 한 달 예산 계획 수정
    DELETE : 한 달 예산 계획 삭제
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
            raise PermissionDenied("본인만 접근 가능합니다.")

        return get_object_or_404(MonthlyPlan, owner=user)

    def get(self, request, owner):
        monthly_plan = self.get_object(request, owner)
        serializer = MonthlyPlanSerializer(monthly_plan)
        return Response(serializer.data)

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
    GET : 오늘 사용 내역 조회
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, owner):
        user = get_object_or_404(User, username=owner)

        if user != request.user:
            raise PermissionDenied("본인만 접근 가능합니다.")

        today = timezone.localtime().date()
        today_plan = TodayPlan.objects.filter(owner=user, date=today).first()
        if today_plan is None:
            return Response(
                {"message": "오늘 사용 내역이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TodayPlanSerializer(today_plan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    