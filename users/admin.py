from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "last_name",
        "first_name",
        "is_staff",
        "is_active",
    )
    search_fields = (
        "email",
        "last_name",
        "first_name",
    )
    list_filter = ("is_staff",)
    fields = (
        "email",
        "last_name",
        "first_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        ("date_joined", "last_login"),
    )
    filter_horizontal = ("groups",)
