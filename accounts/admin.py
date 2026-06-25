from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from functions.common import mark_user_for_force_logout
from .models import User, Notification


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "user_type",
        "is_active",
        "is_staff",
        "created_date",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "user_type")
    search_fields = ("email", "username", "first_name", "last_name", "phone_number")
    ordering = ("-created_date",)
    readonly_fields = ("created_date", "updated_date")
    actions = ("activate_users", "deactivate_users")

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Job Portal Details",
            {
                "fields": (
                    "phone_number",
                    "country_code",
                    "user_type",
                    "phone_otp",
                    "email_otp",
                    "otp_expiration",
                    "retries_otp",
                    "last_otp_request",
                    "created_date",
                    "updated_date",
                )
            },
        ),
    )

    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            "Job Portal Details",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "country_code",
                    "user_type",
                    "is_active",
                )
            },
        ),
    )

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) activated.")

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        user_ids = list(queryset.values_list("id", flat=True))
        updated = queryset.update(is_active=False)
        for user_id in user_ids:
            mark_user_for_force_logout(user_id)
        self.message_user(request, f"{updated} user(s) deactivated and logged out.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.is_active:
            mark_user_for_force_logout(obj.id)


admin.site.register(Notification)
