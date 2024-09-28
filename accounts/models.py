from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, null=True, blank=True)  
    phone_otp = models.CharField(max_length=6, null=True, blank=True)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    
