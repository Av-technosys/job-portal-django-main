from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token

from constants.accounts import SUCCESS_OTP_VERIFICATION_PENDING_APPROVAL
from constants.errors import ERROR_USER_INACTIVE

from .models import User
from .serializers import LoginSerializer, VerifyOtpSerializer


class VerifyOtpSerializerTests(TestCase):
    def test_recruiter_stays_inactive_after_otp_verification(self):
        user = User.objects.create_user(
            username="recruiter@example.com",
            email="recruiter@example.com",
            password="pass12345",
            user_type=2,
            is_active=False,
            email_otp="123456",
            otp_expiration=timezone.now() + timedelta(minutes=10),
        )

        serializer = VerifyOtpSerializer(
            data={"email": user.email, "email_otp": "123456"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        response = serializer.save()
        user.refresh_from_db()

        self.assertFalse(user.is_active)
        self.assertEqual(
            response["message"], SUCCESS_OTP_VERIFICATION_PENDING_APPROVAL
        )
        self.assertFalse(Token.objects.filter(user=user).exists())

    def test_inactive_recruiter_login_returns_admin_contact_message(self):
        User.objects.create_user(
            username="recruiter@example.com",
            email="recruiter@example.com",
            password="pass12345",
            user_type=2,
            is_active=False,
        )

        serializer = LoginSerializer(
            data={"email": "recruiter@example.com", "password": "pass12345"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["message"][0], ERROR_USER_INACTIVE)
