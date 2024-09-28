# accounts/serializers.py
from rest_framework import serializers
from .models import User
from constants.errors import ERROR_INVALID_CREDENTIALS
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(username=validated_data["email"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


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

        raise serializers.ValidationError({"error": ERROR_INVALID_CREDENTIALS})
