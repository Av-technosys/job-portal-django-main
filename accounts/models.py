from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from constants.common import USER_TYPE
from constants.user_profiles import NOTIFICATION_TYPE_CHOICES
from payment.models import Plan

user_type = models.CharField(
    max_length=20,
    choices=[
        ("admin", "Admin"),
        ("recruiter", "Recruiter"),
        ("job_seeker", "Job Seeker"),
    ],
    default="job_seeker",
)


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE, null=True, blank=True
    )
    phone_otp = models.CharField(max_length=6, null=True, blank=True)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(blank=True, null=True)
    retries_otp = models.PositiveIntegerField(default=0)
    last_otp_request = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"], name="user_email_index"),
        ]


class Notification(models.Model):
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    body = models.CharField(max_length=255)
    sent_from = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_from"
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_by",
    )
    meta_data = models.JSONField(null=True, blank=True)
    read_status = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["received_by"], name="noti_received_by_index"),
            models.Index(fields=["created_date"], name="noti_created_date_index"),
        ]

    def __str__(self):
        return f"Notification for {self.received_by.username}"


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="s_fk_user"
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="plan")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["plan"], name="plan_index"),
        ]

        def __str__(self):
            return f"{self.user} subscribed {self.plan}"


class ContactUs(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
