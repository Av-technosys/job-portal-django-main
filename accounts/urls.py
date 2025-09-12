from django.urls import path
from .views import (
    account_details,
    list_notifications,
    register_user,
    resend_otp,
    reset_password_otp,
    user_login,
    user_logout,
    verify_otp,
    verify_reset_password,
    sso_user,
    remove_user,
    set_user_activate,
    set_user_deactivate,
    create_contact_us
)

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", user_login, name="login"),
    path("activate/", set_user_activate, name="set_user_activate"),
    path("deactivate/", set_user_deactivate, name="set_user_deactivate"),
    path("contacts/", create_contact_us, name="create_contact"),
    path("logout/", user_logout, name="logout"),
    path("verify_otp/", verify_otp, name="verify_otp"),
    path(
        "send_otp_password_reset/",
        reset_password_otp,
        name="send_otp_password_reset",
    ),
    path(
        "resend_otp/",
        resend_otp,
        name="resend_otp",
    ),
    path(
        "verify_otp_password_reset/",
        verify_reset_password,
        name="verify_otp_password_reset",
    ),
    path("details/", account_details, name="account_details"),
    path("notifications/", list_notifications, name="list_notification"),
    path("sso/", sso_user, name="sso"),
    path("remove_user/", remove_user, name="remove_user")
]
