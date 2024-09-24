from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  
    otp = models.CharField(max_length=6, null=True, blank=True)
    
    def __str__(self):
        return self.username
