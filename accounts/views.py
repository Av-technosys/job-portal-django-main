from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from handlers.permissions import IsAdmin
from accounts.models import User , ContactUs
from functions.fcm import list_notification
from user_profiles.models import FCMToken
from .serializers import (
    LoginSerializer,
    NotificationSerializer,
    ResendOtpSerializer,
    ResetPasswordSendOtpSerializer,
    SSOUserSerializer,
    UserMetaSerializer,
    UserSerializer,
    VerifyOtpAndChangePasswordSerializer,
    VerifyOtpSerializer,
    ContactUSSerializer,
    AdminUserSerializer
)
from constants.errors import ERROR_LOGOUT_FAILED
from constants.accounts import SUCCESS_LOGOUT
from functions.common import (
    ResponseHandler,
    serializer_handle,
    serializer_handle_customize_response,
    serializer_handle_customize_response_only_validate,
    get_customize_handler,
    delete_handle,
    user_status_handle,
    create_new_handler,
    list_all_items_handler,
    get_all_admin_details
)


@api_view(["POST"])
def register_user(request):
    return serializer_handle(UserSerializer, request)


@api_view(["POST"])
def sso_user(request):
    return serializer_handle_customize_response(SSOUserSerializer, request)


@api_view(["POST"])
def remove_user(request):
    return delete_handle(User, request)


@api_view(["POST"])
def set_user_activate(request): 
    return user_status_handle(User, request, True)


@api_view(["POST"])
def set_user_deactivate(request):
    return user_status_handle(User, request, False)

@api_view(["POST"])
def create_contact_us(request):
    return create_new_handler(ContactUSSerializer, request)


@api_view(["GET"])
def get_contact(request):
    return list_all_items_handler(ContactUs, ContactUSSerializer, request)

@api_view(["POST"])
def user_login(request):
    return serializer_handle_customize_response_only_validate(LoginSerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    try:
        request.user.auth_token.delete()
        instances = FCMToken.objects.filter(user=request.user)
        if instances.exists():
            instances.delete()
        return ResponseHandler.success(
            data={"message": SUCCESS_LOGOUT}, status_code=status.HTTP_200_OK
        )
    except Exception:
        return ResponseHandler.error(
            message=ERROR_LOGOUT_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def verify_otp(request):
    return serializer_handle_customize_response(VerifyOtpSerializer, request)


@api_view(["POST"])
def reset_password_otp(request):
    return serializer_handle_customize_response(ResetPasswordSendOtpSerializer, request)


# ResendOTP
@api_view(["POST"])
def resend_otp(request):
    return serializer_handle_customize_response(ResendOtpSerializer, request)


@api_view(["POST"])
def verify_reset_password(request):
    return serializer_handle_customize_response(
        VerifyOtpAndChangePasswordSerializer, request
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def account_details(request):
    return get_customize_handler(
        User, UserMetaSerializer, {"email": request.user}, request
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    return list_notification(NotificationSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def get_all_admin(request):
    return get_all_admin_details(User, AdminUserSerializer, request)