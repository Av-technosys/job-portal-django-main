# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from .serializers import UserSerializer,LoginSerializer,VerifyOtpSerializer
from constants.errors import ERROR_LOGOUT_FAILED,FAILED_REGISTRATION
from constants.accounts import SUCCESS_LOGOUT,SUCCESS_REGISTRATION

@api_view(['POST'])  
def register_user(request):  
    serializer = UserSerializer(data=request.data)  
    try:  
        if serializer.is_valid():  
            serializer.save()  
            return Response({"message": SUCCESS_REGISTRATION}, status=status.HTTP_201_CREATED)  
        else:  
            return Response({"message": FAILED_REGISTRATION, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)  
    except Exception as e:  
        return Response({ "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

@api_view(['POST'])
def user_login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token_data = serializer.authenticate_user(serializer.validated_data)
    return Response(token_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        request.user.auth_token.delete()
        return Response({"message": SUCCESS_LOGOUT}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": ERROR_LOGOUT_FAILED}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])  # OTP verification should not require the user to be authenticated
def verify_otp(request):
    serializer = VerifyOtpSerializer(data=request.data)
    
    if serializer.is_valid():
        result = serializer.save()  # Serializer handles the logic
        return Response(result, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
