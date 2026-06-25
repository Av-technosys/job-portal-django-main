from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from constants.errors import ERROR_USER_INACTIVE
from functions.common import user_status_handle

from .models import User
from .serializers import LoginSerializer, VerifyOtpSerializer


class VerifyOtpSerializerTests(TestCase):
    def test_recruiter_becomes_active_after_otp_verification(self):
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

        self.assertTrue(user.is_active)
        self.assertEqual(response["token"], Token.objects.get(user=user).key)

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

    def test_deactivation_marks_user_for_force_logout(self):
        user = User.objects.create_user(
            username="jobseeker@example.com",
            email="jobseeker@example.com",
            password="pass12345",
            user_type=1,
            is_active=True,
        )
        Token.objects.create(user=user)

        class Request:
            data = {"id": user.id}

        response = user_status_handle(User, Request(), False)
        user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["data"]["force_logout"])
        self.assertFalse(response.data["data"]["is_active"])
        self.assertFalse(user.is_active)
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_deactivated_token_cannot_access_session_status(self):
        user = User.objects.create_user(
            username="active@example.com",
            email="active@example.com",
            password="pass12345",
            user_type=1,
            is_active=True,
        )
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        active_response = client.get("/accounts/session_status/")
        self.assertEqual(active_response.status_code, 200)
        self.assertFalse(active_response.data["data"]["force_logout"])

        user.is_active = False
        user.save()

        inactive_response = client.get("/accounts/session_status/")
        self.assertEqual(inactive_response.status_code, 401)
        self.assertEqual(inactive_response.data["message"], ERROR_USER_INACTIVE)
        self.assertTrue(inactive_response.data["force_logout"])
        self.assertTrue(Token.objects.filter(user=user).exists())
