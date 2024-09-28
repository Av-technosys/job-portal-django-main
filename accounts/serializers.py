from rest_framework import serializers
from .models import User
from constants.errors import (
    ERROR_INVALID_CREDENTIALS,
    FAILED_SEND_OTP,
    ERROR_OTP_VERIFICATION_FAILED,
    ERROR_USER_NOT_FOUND,
    ERROR_USER_EXIST,
    ERROR_OTP_EXPIRED,
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from twilio.rest import Client
from django.conf import settings
from functions.common import generate_otp, ResponseHandler
from constants.accounts import (
    SUCCESS_OTP_VERIFICATION,
    OTP_MESSAGE,
    EMAIL_OTP_SUBJECT,
    USER_REGISTERED,
    EMAIL_OTP_MESSAGE_TEMPLATE,
)
from dotenv import load_dotenv
import os
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta


load_dotenv()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "phone_number"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        email = validated_data["email"]
        phone_number = validated_data["phone_number"]
        password = validated_data["password"]

        # Check if the user already exists but is inactive
        user = User.objects.filter(email=email).first()

        if user and not user.is_active:
            phone_otp = generate_otp()
            email_otp = generate_otp()

            # Ensure both OTPs are different
            while email_otp == phone_otp:
                email_otp = generate_otp()

                # Update the OTP and expiration time
            user.phone_otp = phone_otp
            user.email_otp = email_otp
            user.otp_expiration = timezone.now() + timedelta(minutes=10)

            # Resend OTPs
            self.send_phone_otp(phone_number, phone_otp)
            self.send_email_otp(email, email_otp)

            # Save the updated user
            user.save()

            return ResponseHandler.success(data={"message": USER_REGISTERED})

        # If user doesn't exist, proceed with normal registration
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"message": ERROR_USER_EXIST})

        phone_otp = generate_otp()
        email_otp = generate_otp()

        # Ensure both OTPs are different
        while email_otp == phone_otp:
            email_otp = generate_otp()

        # Set OTP expiration time to 10 minutes from now
        otp_expiration = timezone.now() + timedelta(minutes=10)

        validated_data["username"] = email
        user = User(
            **validated_data,
            phone_otp=phone_otp,
            email_otp=email_otp,
            otp_expiration=otp_expiration,
        )
        user.set_password(password)
        user.is_active = False
        user.save()

        # Send OTP via SMS and Email
        self.send_phone_otp(phone_number, phone_otp)
        self.send_email_otp(email, email_otp)

        return ResponseHandler.success(data={"message": USER_REGISTERED})

    def send_email_otp(self, email, otp):
        subject = EMAIL_OTP_SUBJECT
        message = EMAIL_OTP_MESSAGE_TEMPLATE.format(otp=otp)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            raise serializers.ValidationError(
                {"error": f"Failed to send OTP via email: {str(e)}"}
            )

    def send_phone_otp(self, phone_number, otp):
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        try:
            message = client.messages.create(
                body=f"{OTP_MESSAGE} {otp}",
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=phone_number,
            )
        except Exception as e:
            raise serializers.ValidationError({"error": FAILED_SEND_OTP.format(e)})


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def authenticate_user(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        user = authenticate(username=email, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return {"Token": token.key}

        return serializers.ValidationError(message=ERROR_INVALID_CREDENTIALS)


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Validates the user's email
    email_otp = serializers.CharField(max_length=6)
    phone_otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email, email_otp, phone_otp = data.values()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": ERROR_USER_NOT_FOUND})

        # Check if OTPs are expired
        if not user.otp_expiration or timezone.now() > user.otp_expiration:
            raise serializers.ValidationError({"message": ERROR_OTP_EXPIRED})

        # Validate OTPs
        if user.email_otp != email_otp or user.phone_otp != phone_otp:
            raise serializers.ValidationError(
                {"message": ERROR_OTP_VERIFICATION_FAILED}
            )

        return data  # Return validated data if both OTPs are correct

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        # Activate user account
        user.is_active = True
        user.phone_otp = None
        user.email_otp = None
        user.otp_expiration = None  # Clear expiration time as OTPs are used
        user.save()

        return ResponseHandler.success(
            data={
                "message": SUCCESS_OTP_VERIFICATION,
                "user": {
                    "email": user.email,
                    "phone_number": user.phone_number,
                },
            }
        )
