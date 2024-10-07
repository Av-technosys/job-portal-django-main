from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.models import User
from .serializers import (
    UserSerializer,
    LoginSerializer,
    VerifyOtpSerializer,
    ResetPasswordSendOtpSerializer,
    VerifyOtpAndChangePasswordSerializer,
)
from constants.errors import ERROR_LOGOUT_FAILED
from constants.accounts import SUCCESS_LOGOUT
from functions.common import (
    ResponseHandler,
    serializer_handle,
    serializer_handle_customize_response,
    serializer_handle_customize_response_only_validate,
    get_customize_handler,
)


@api_view(["POST"])
def register_user(request):
    return serializer_handle(UserSerializer, request)


@api_view(["POST"])
def user_login(request):
    return serializer_handle_customize_response_only_validate(LoginSerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        request.user.auth_token.delete()
        return ResponseHandler.success(
            data={"message": SUCCESS_LOGOUT}, status_code=status.HTTP_200_OK
        )
    except Exception:
        return ResponseHandler.error(
            message=ERROR_LOGOUT_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    return serializer_handle_customize_response(VerifyOtpSerializer, request)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_otp(request):
    return serializer_handle_customize_response(ResetPasswordSendOtpSerializer, request)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_reset_password(request):
    return serializer_handle_customize_response(
        VerifyOtpAndChangePasswordSerializer, request
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def account_details(request):
    return get_customize_handler(User, UserSerializer, {"email": request.user})
