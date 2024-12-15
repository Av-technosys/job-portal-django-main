from rest_framework import serializers
from constants.accounts import (
    EMAIL_OTP_SUBJECT,
    EMAIL_OTP_MESSAGE_TEMPLATE,
)
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from constants.job_application import (
    JOB_SEEKER_APPLICATION_CONFIRMATION_SUBJECT,
    RECRUITER_CONFIRMATION_SUBJECT,
)
from constants.common import JOB_ASSURED_LOGO
from functions.common import get_todays_date


def send_email_core_fucntion(
    subject, message, from_email, recipient_list, html_message
):
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def send_email_otp(email, otp):
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


def send_application_confirmation_to_job_seeker(
    student_details, recruiter_details, job_details
):
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student_details.email]

    subject = JOB_SEEKER_APPLICATION_CONFIRMATION_SUBJECT
    html_message = render_to_string(
        "email_templates/job_seeker_application_email.html",
        {
            "job_seeker_name": student_details.first_name,
            "job_title": job_details.department,
            "company_name": recruiter_details.company_name,
            "company_email": recruiter_details.company_email,
            "website_url": recruiter_details.company_url,
            "logo_url": JOB_ASSURED_LOGO,
        },
    )

    plain_message = strip_tags(html_message)

    try:
        send_email_core_fucntion(
            subject, plain_message, from_email, recipient_list, html_message
        )
    except Exception as e:
        raise serializers.ValidationError(
            {
                "error": f"Failed to send_application_confirmation_to_job_seeker via email: {str(e)}"
            }
        )


def send_application_received_to_recruiter(
    student_details, recruiter_details, job_details
):
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [recruiter_details.company_email]

    subject = RECRUITER_CONFIRMATION_SUBJECT
    html_message = render_to_string(
        "email_templates/recruiter_application_email.html",
        {
            "job_seeker_name": student_details.first_name,
            "job_seeker_email": student_details.email,
            "job_title": job_details.department,
            "application_date": get_todays_date(),
            "company_name": recruiter_details.company_name,
            "company_email": recruiter_details.company_email,
            "website_url": recruiter_details.company_url,
            "logo_url": JOB_ASSURED_LOGO,
        },
    )

    plain_message = strip_tags(html_message)

    try:
        send_email_core_fucntion(
            subject, plain_message, from_email, recipient_list, html_message
        )
    except Exception as e:
        raise serializers.ValidationError(
            {
                "error": f"Failed to send_application_received_to_recruiter via email: {str(e)}"
            }
        )
