# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from .serializers import UserSerializer
from .models import User
from constants.errors import ERROR_INVALID_CREDENTIALS, ERROR_LOGOUT_FAILED
from constants.accounts import SUCCESS_LOGOUT
from functions.common import get_login_request_payload


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def user_login(request):
    username = get_login_request_payload(request, 'username')
    password = get_login_request_payload(request, 'password')

    user = None
    if '@' in username:
        try:
            user = User.objects.get(email=username)
        except ObjectDoesNotExist:
            pass

    if not user:
        user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

    return Response({'error': ERROR_INVALID_CREDENTIALS}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': SUCCESS_LOGOUT}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': ERROR_LOGOUT_FAILED}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
