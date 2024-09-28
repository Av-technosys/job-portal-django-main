from rest_framework import status  
from rest_framework.decorators import api_view, permission_classes  
from rest_framework.permissions import IsAuthenticated, AllowAny  
from .serializers import UserSerializer, LoginSerializer, VerifyOtpSerializer  
from constants.errors import ERROR_LOGOUT_FAILED
from constants.accounts import SUCCESS_LOGOUT
from functions.common import ResponseHandler, serializer_handle  

@api_view(['POST'])  
def register_user(request):  
    return serializer_handle(UserSerializer, request)  

@api_view(['POST'])  
def user_login(request):  
    try:  
        serializer = LoginSerializer(data=request.data)  
        serializer.is_valid(raise_exception=True)  # This will raise an error automatically  
        token_data = serializer.authenticate_user(serializer.validated_data)  
        return ResponseHandler.success(data=token_data, status_code=status.HTTP_200_OK)  
    
    except Exception as e:  
        # You can log the exception if needed  
        return ResponseHandler.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)  

@api_view(['POST'])  
@permission_classes([IsAuthenticated])  
def user_logout(request):  
    try:  
        request.user.auth_token.delete()  
        return ResponseHandler.success(data={"message": SUCCESS_LOGOUT}, status_code=status.HTTP_200_OK)  
    except Exception as e:  
        return ResponseHandler.error(message=ERROR_LOGOUT_FAILED, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)  

@api_view(['POST'])  
@permission_classes([AllowAny])  
def verify_otp(request):  
    return serializer_handle(VerifyOtpSerializer, request)