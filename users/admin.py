from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "username",
        "is_active",
        "is_staff",
        "is_admin",
        "date_joined",
        "last_login",
    )
    list_display_links = ("pk", "username")

    ordering = ("-date_joined",)
