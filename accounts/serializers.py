from rest_framework import serializers
from .models import Notification, User
from constants.common import USER_TYPE
from constants.errors import (
    ERROR_INVALID_CREDENTIALS,
    ERROR_OTP_VERIFICATION_FAILED,
    ERROR_USER_NOT_FOUND,
    ERROR_USER_EXIST,
    ERROR_OTP_EXPIRED,
    ERROR_NEW_PASSWORD_NOT_FOUND,
    OTP_LIMIT_REACHED_ERROR,
    ALREADY_SAVED,
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from functions.common import (
    generate_otp,
    generate_password_string,
    get_job_seeker_profile_image,
    get_recruiter_profile_image,
    is_job_seeker,
    ResponseHandler,
)
from constants.accounts import (
    PASSWORD_RESET,
    REGISTRATION_META_FIELDS,
    SUCCESS_SENDING_OTP,
    USER_META_FIELDS,
)
from django.utils import timezone
from datetime import timedelta
from functions.send_email import send_auto_generated_password, send_email_otp
from functions.send_otp import send_phone_otp
from accounts.models import Subscription


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


class UserMetaSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    access_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = USER_META_FIELDS

    def get_profile_picture(self, obj):
        request = self.context.get("request")
        if is_job_seeker(request):
            return get_job_seeker_profile_image(obj)
        return get_recruiter_profile_image(obj)

    def get_access_type(self, obj):
        subscription_data = obj.s_fk_user.first()
        if subscription_data is not None:
            return subscription_data.plan_id
        return None


class SSOUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=150)
    user_type = serializers.ChoiceField(choices=USER_TYPE)

    def save(self):
        email = self.validated_data["email"]
        name = self.validated_data["name"]
        user_type = self.validated_data["user_type"]

        user = User.objects.filter(email=email).first()

        if user and user.is_active:
            pass

        elif user and not user.is_active:
            user.is_active = True
            user.save()

        else:
            user = User(
                username=email,
                email=email,
                is_active=True,
                first_name=name,
                user_type=user_type,
                country_code="+91",
            )
            auto_generated_password = generate_password_string()
            user.set_password(auto_generated_password)
            user.save()

            # Send password via email
            send_auto_generated_password(email, auto_generated_password)

        # Generate or return a token for the user
        token, _ = Token.objects.get_or_create(user=user)

        if token:
            return {"token": token.key}
        else:
            raise ResponseHandler.api_exception_error()


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


class ResetPasswordSendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": ERROR_USER_NOT_FOUND})
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        # Generate OTP and set OTP expiration time (10 minutes from now)
        # phone_otp = generate_otp()
        email_otp = generate_otp()
        otp_expiration = timezone.now() + timedelta(minutes=10)

        user.email_otp = email_otp
        user.otp_expiration = otp_expiration
        user.save()

        # Send OTP via email or phone
        send_email_otp(email, email_otp)
        # send_phone_otp(user.phone_number, user.phone_otp)

        return {"message": SUCCESS_SENDING_OTP}


# resend otp
class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": ERROR_USER_NOT_FOUND})

        if user.last_otp_request and timezone.now() < user.last_otp_request + timedelta(
            minutes=10
        ):
            # If within an hour, check the retries_otp count
            if user.retries_otp >= 3:
                raise ResponseHandler.api_exception_error(
                    message=OTP_LIMIT_REACHED_ERROR
                )
        else:
            # Reset retries_otp if one hour has passed
            user.retries_otp = 0
            user.save()
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        # Generate OTP and set OTP expiration time (10 minutes from now)
        # phone_otp = generate_otp()
        # Increment retries_otp and update last_otp_request
        user.retries_otp += 1
        user.last_otp_request = timezone.now()
        # Generate OTP and set expiration time (10 minutes from now)
        email_otp = generate_otp()
        otp_expiration = timezone.now() + timedelta(minutes=10)

        user.email_otp = email_otp
        user.otp_expiration = otp_expiration
        user.save()
        # Send OTP via email or phone
        send_email_otp(email, email_otp)
        # send_phone_otp(user.phone_number, user.phone_otp)
        return {"message": SUCCESS_SENDING_OTP}


class VerifyOtpAndChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    email_otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        email = data.get("email")
        email_otp = data.get("email_otp")
        new_password = data.get("new_password")

        if not new_password:
            return serializers.ValidationError(
                {"message": ERROR_NEW_PASSWORD_NOT_FOUND}
            )

        # Retrieve user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": ERROR_USER_NOT_FOUND})

        # Check if OTP is valid and not expired
        if user.email_otp != email_otp:
            raise serializers.ValidationError(
                {"message": ERROR_OTP_VERIFICATION_FAILED}
            )
        if not user.otp_expiration or timezone.now() > user.otp_expiration:
            raise serializers.ValidationError({"message": ERROR_OTP_EXPIRED})

        # if user.phone_otp != phone_otp:
        #     raise serializers.ValidationError({"message": "Invalid OTP"})
        # if not user.otp_expiration or timezone.now() > user.otp_expiration:
        #     raise serializers.ValidationError({"message": "OTP has expired"})

        return data

    def save(self):
        email = self.validated_data["email"]
        new_password = self.validated_data["new_password"]

        user = User.objects.get(email=email)

        # Set new password and clear OTP fields
        user.set_password(new_password)
        user.email_otp = None
        user.otp_expiration = None
        user.save()

        return {"message": PASSWORD_RESET}


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
