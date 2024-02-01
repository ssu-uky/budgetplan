from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "owner",
        "pay_type",
        "pay_title",
        "pay_price",
        "pay_date",
    )
    list_display_links = ("pk", "owner")
