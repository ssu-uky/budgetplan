from django.db import models

from users.models import User
from payments.models import Payment


class MonthlyPlan(models.Model):
    """
    한 달 예산 계획 모델
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="monthly_plans",
        verbose_name="사용자",
        blank=False,
    )

    # 한달 수입 (monthly_income = monthly_possible + monthly_saving)
    monthly_income = models.PositiveIntegerField(
        blank=False,
    )

    # 한달 저축 금액 (monthly_saving = monthly_income - monthly_possible)
    monthly_saving = models.PositiveIntegerField(
        blank=False,
    )

    # 한달 지출 목록
    monthly_spending = models.ManyToManyField(
        Payment,
        related_name="monthly_spending",
        blank=True,
    )

    # 한달 총 지출 금액
    monthly_total_spending = models.PositiveIntegerField(
        default=0,
    )

    # 한달 지출 가능 금액 (monthly_possible = monthly_income - monthly_saving)
    monthly_possible = models.PositiveIntegerField(
        blank=False,
    )

    def __str__(self):
        return f"{self.owner.name}님, 이번 달 사용 가능 금액은 {self.monthly_possible}원 입니다."


class TodayPlan(models.Model):
    """
    하루 예산 계획 모델
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="today_plans",
        verbose_name="사용자",
        blank=False,
    )

    # 하루 지출 목록
    today_spending = models.ManyToManyField(
        Payment,
        related_name="today_spending",
        blank=True,
    )

    # 하루 총 지출 금액
    today_total_spending = models.PositiveIntegerField(
        default=0,
    )

    # 하루 지출 가능 금액
    today_possible = models.PositiveIntegerField(
        default=0,
    )

    def __str__(self):
        return f"{self.owner.name}님, 오늘의 예산 계획은 {self.today_possible}원 입니다."
