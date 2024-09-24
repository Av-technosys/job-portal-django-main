# accounts/serializers.py
from rest_framework import serializers
from .models import User
from constants.errors import ERROR_INVALID_CREDENTIALS,FAILED_SEND_OTP,ERROR_OTP_VERIFICATION_FAILED,ERROR_USER_NOT_FOUND
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from twilio.rest import Client
from django.conf import settings
from twilio.base.exceptions import TwilioRestException
import random
from constants.accounts import SUCCESS_OTP_VERIFICATION,OTP_MESSAGE
from dotenv import load_dotenv
import os

load_dotenv()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP
        # Create user
        user = User(
            email=validated_data['email'],
            username=validated_data['email'],  
            phone_number=validated_data['phone_number'],
            otp=otp
        )
        user.set_password(validated_data['password'])
        user.is_active = False  # User account inactive until OTP verification
        user.save()

        # Generate OTP
      
        
        # Send OTP via SMS
        self.send_phone_otp(user.phone_number, otp)
       
        return {
            'email':user.email
        }

    def send_email_otp(self, email, otp):
        # Implement email sending logic here
        pass

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
            return message.sid  # Return SID to confirm message was sent
        except Exception as e:
            raise serializers.ValidationError({'error': FAILED_SEND_OTP.format(e)})

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def authenticate_user(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        user = authenticate(username=email, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return {'token': token.key}

        raise serializers.ValidationError({'error': ERROR_INVALID_CREDENTIALS})
    
class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': ERROR_USER_NOT_FOUND})


        if user.otp != otp:
            raise serializers.ValidationError({'error': ERROR_OTP_VERIFICATION_FAILED})
        
        return data

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        # Activate user account after successful OTP verification
        user.is_active = True
        user.otp = None  
        user.save()

        return {
            'message': SUCCESS_OTP_VERIFICATION,
            'user': {
                'email': user.email,
                'phone_number': user.phone_number,
            }
        }