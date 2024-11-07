from django.urls import path
from .views import (
    register_user,
    user_login,
    user_logout,
    verify_otp,
    reset_password_otp,
    resend_otp,
    verify_reset_password,
    account_details,
)

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("verify_otp/", verify_otp, name="verify_otp"),
    path(
        "send_otp_password_reset/",
        reset_password_otp,
        name="send_otp_password_reset",
    ),
    path(
        "resend_otp_password_reset/",
        resend_otp,
        name="resend_otp_password_reset",
    ),
    path(
        "verify_otp_password_reset/",
        verify_reset_password,
        name="verify_otp_password_reset",
    ),
    path("details/", account_details, name="account_details"),
]
