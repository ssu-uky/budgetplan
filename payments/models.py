from django.db import models
from django.utils import timezone

from users.models import User


class Payment(models.Model):
    """
    지출 내역 모델
    """

    class PayChoices(models.TextChoices):
        FOOD = "Food", "식비"
        CAFE = "Cafe", "카페"
        CLOTHES = "Clothes", "의류"
        PHONE = "Phone", "통신비"
        TRANSPORT = "Transport", "교통비"
        TRAVEL = "Travel", "여행"
        CULTURE = "Culture", "문화"
        HEALTH = "Health", "건강"
        BEAUTY = "Beauty", "미용"
        EDUCATION = "Education", "교육"
        PRESENT = "Present", "선물"
        ETC = "Etc", "기타"

    owner = models.ForeignKey(
        User,
        related_name="payments",
        on_delete=models.CASCADE,
        blank=False,
    )

    # 지출 종류
    pay_type = models.CharField(
        max_length=15,
        choices=PayChoices.choices,
        default=PayChoices.FOOD,
        blank=False,
    )

    # 지출 제목
    pay_title = models.CharField(
        max_length=50,
        blank=False,
    )

    # 지출 내용
    pay_content = models.TextField(
        max_length=200,
        blank=True,
    )

    # 지출 금액
    pay_price = models.PositiveIntegerField(
        blank=False,
    )

    # 지출 날짜
    pay_date = models.DateField(
        default=timezone.now,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.pay_title} - {self.pay_price}원"
