from django.contrib.auth.models import AbstractUser
from django.db import models
from constants.common import USER_TYPE


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPE, null=True, blank=True
    )
    phone_otp = models.CharField(max_length=6, null=True, blank=True)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
