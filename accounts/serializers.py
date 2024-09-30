from rest_framework import serializers
from .models import User
from constants.errors import (
    ERROR_INVALID_CREDENTIALS,
    ERROR_OTP_VERIFICATION_FAILED,
    ERROR_USER_NOT_FOUND,
    ERROR_USER_EXIST,
    ERROR_OTP_EXPIRED,
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from functions.common import generate_otp, ResponseHandler
from constants.accounts import (
    REGISTRATION_META_FIELDS,
)
from django.utils import timezone
from datetime import timedelta
from functions.send_email import send_email_otp
from functions.send_otp import send_phone_otp


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = REGISTRATION_META_FIELDS
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        email = validated_data["email"]
        phone_number = validated_data["phone_number"]
        password = validated_data["password"]

        user = User.objects.filter(email=email).first()

        # Check if the user already exists & active
        if user and user.is_active:
            raise ResponseHandler.api_exception_error(ERROR_USER_EXIST)

        phone_otp = generate_otp()
        email_otp = generate_otp()

        # Ensure both OTPs are different
        while email_otp == phone_otp:
            email_otp = generate_otp()

        # Set OTP expiration time to 10 minutes from now
        otp_expiration = timezone.now() + timedelta(minutes=10)

        if user and not user.is_active:
            user.email = email
            user.user_type = validated_data["user_type"]
            user.first_name = validated_data["first_name"]
            user.phone_number = phone_number

        else:
            user = User(**validated_data)

        user.username = email
        user.email_otp = email_otp
        user.phone_otp = phone_otp
        user.otp_expiration = otp_expiration

        # This will only be changed, if we want to give all country services
        user.country_code = "+91"

        user.set_password(password)
        user.is_active = False
        user.save()

        # Send OTP via SMS and Email
        # send_phone_otp(phone_number, phone_otp)
        send_email_otp(email, email_otp)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email, _ = data.values()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": ERROR_USER_NOT_FOUND})

        # Check if the user is active
        if not user.is_active:
            raise serializers.ValidationError({"message": ERROR_USER_NOT_FOUND})

        return data

    def return_response(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        # Authenticate the user if they are active
        user = authenticate(username=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return {"token": token.key}
        else:
            raise ResponseHandler.api_exception_error(ERROR_INVALID_CREDENTIALS)


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Validates the user's email
    email_otp = serializers.CharField(max_length=6)
    # phone_otp = serializers.CharField(max_length=6)

    def validate(self, data):
        # email, email_otp, phone_otp = data.values()
        email, email_otp = data.values()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": ERROR_USER_NOT_FOUND})

        # Check if OTPs are expired
        if not user.otp_expiration or timezone.now() > user.otp_expiration:
            raise serializers.ValidationError({"message": ERROR_OTP_EXPIRED})

        # Validate OTPs
        # if user.email_otp != email_otp or user.phone_otp != phone_otp:
        if user.email_otp != email_otp:
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

        token, _ = Token.objects.get_or_create(user=user)
        if token:
            return {"token": token.key}
        else:
            raise ResponseHandler.api_exception_error()
