from rest_framework import serializers
from constants.accounts import (
    EMAIL_OTP_SUBJECT,
    EMAIL_OTP_MESSAGE_TEMPLATE,
)
from django.core.mail import send_mail
from django.conf import settings


def send_email_core_fucntion(subject, message, from_email, recipient_list):
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


def send_email_otp(self, email, otp):
    subject = EMAIL_OTP_SUBJECT
    message = EMAIL_OTP_MESSAGE_TEMPLATE.format(otp=otp)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_email_core_fucntion(subject, message, from_email, recipient_list)
    except Exception as e:
        raise serializers.ValidationError(
            {"error": f"Failed to send OTP via email: {str(e)}"}
        )
