# accounts/serializers.py
from rest_framework import serializers
from .models import User
from constants.errors import ERROR_INVALID_CREDENTIALS,FAILED_SEND_OTP,ERROR_OTP_VERIFICATION_FAILED,ERROR_USER_NOT_FOUND,ERROR_USER_EXIST
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from twilio.rest import Client
from django.conf import settings
from functions.common import generate_otp
from constants.accounts import SUCCESS_OTP_VERIFICATION,OTP_MESSAGE,EMAIL_OTP_SUBJECT,USER_REGISTERED,EMAIL_OTP_MESSAGE_TEMPLATE
from dotenv import load_dotenv
import os
from django.core.mail import send_mail

load_dotenv()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", 'phone_number']
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
         # Generate phone OTP
        phone_otp = generate_otp()
        email_otp = generate_otp()

        if User.objects.filter(email=validated_data['email']).exists():  
            raise serializers.ValidationError({"message": ERROR_USER_EXIST })  


        #ensuring both otp are not same
        while email_otp == phone_otp:
            email_otp = generate_otp()

        validated_data['username'] = validated_data.get('email')

        # Create user
        user = User(**validated_data, phone_otp=phone_otp, email_otp=email_otp)
        user.set_password(validated_data['password'])
        user.is_active = False
        user = User(username=validated_data["email"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()

        # Send OTP via SMS
        self.send_phone_otp(user.phone_number,phone_otp )

        # Send OTP via Email
        self.send_email_otp(user.email, email_otp)


    def send_email_otp(self, email, otp):
        load_dotenv()
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
            raise serializers.ValidationError({'error': f"Failed to send OTP via email: {str(e)}"})

    def send_phone_otp(self, phone_number, otp):
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        try:
            message = client.messages.create(
                body=f'{OTP_MESSAGE} {otp}',
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                to=phone_number
            )
        except Exception as e:
            raise serializers.ValidationError({'error': FAILED_SEND_OTP.format(e)})


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def authenticate_user(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        user = authenticate(username=email, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return {"token": token.key}

        raise serializers.ValidationError({'error': ERROR_INVALID_CREDENTIALS})
    
class VerifyOtpSerializer(serializers.Serializer):
    email_otp = serializers.CharField(max_length=6)  
    phone_otp = serializers.CharField(max_length=6)  

    def validate(self, data):

        email, email_otp, phone_otp = data.values()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': ERROR_USER_NOT_FOUND})

        # Validate email OTP
        if user.email_otp != email_otp:
            raise serializers.ValidationError({'error': ERROR_OTP_VERIFICATION_FAILED})

        # Validate phone OTP
        if user.phone_otp != phone_otp:
            raise serializers.ValidationError({'error': ERROR_OTP_VERIFICATION_FAILED})


    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        # Activate user account after both OTPs are successfully verified
        user.is_active = True

        # Clear both OTPs after successful verification
        user.phone_otp = None
        user.email_otp = None
        user.save()

        return {
            'message': SUCCESS_OTP_VERIFICATION,
            'user': {
                'email': user.email,
                'phone_number': user.phone_number,
            }
        }
