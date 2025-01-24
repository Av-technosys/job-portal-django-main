from rest_framework import serializers
from constants.accounts import (
    AUTO_GENERATE_PASSWORD_SUBJECT,
    AUTO_GENERATE_PASSWORD_TEMPLATE,
    EMAIL_OTP_MESSAGE_TEMPLATE,
    EMAIL_OTP_SUBJECT,
)
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from constants.job_application import (
    JOB_SEEKER_APPLICATION_CONFIRMATION_SUBJECT,
    RECRUITER_CONFIRMATION_SUBJECT,
)
from constants.common import JOB_ASSURED_LOGO, COMPANY_EMAIL, COMPANY_NAME, COMPANY_URL
from functions.common import get_todays_date
from django.utils.timezone import now
from constants.payment import SUBJECT
from functions.common import generate_pdf


def send_email_core_fucntion(
    subject, message, from_email, recipient_list, html_message=""
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


def send_auto_generated_password(email, password):
    subject = AUTO_GENERATE_PASSWORD_SUBJECT
    message = AUTO_GENERATE_PASSWORD_TEMPLATE.format(password=password)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_email_core_fucntion(subject, message, from_email, recipient_list)
    except Exception as e:
        raise serializers.ValidationError(
            {"error": f"Failed to send auto generated otp via email: {str(e)}"}
        )


def send_application_confirmation_to_job_seeker(
    student_details, recruiter_details, job_details, recruiter_personal_details
):
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student_details.email]

    subject = JOB_SEEKER_APPLICATION_CONFIRMATION_SUBJECT
    html_message = render_to_string(
        "email_templates/job_seeker_application_email.html",
        {
            "job_seeker_name": student_details.first_name,
            "job_title": job_details.role,
            "company_name": recruiter_personal_details.first_name,
            "company_email": recruiter_personal_details.email,
            "website_url": recruiter_details.company_website,
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
    student_details, recruiter_details, job_details, recruiter_personal_details
):
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [recruiter_personal_details.email]

    subject = RECRUITER_CONFIRMATION_SUBJECT
    html_message = render_to_string(
        "email_templates/recruiter_application_email.html",
        {
            "job_seeker_name": student_details.first_name,
            "job_seeker_email": student_details.email,
            "job_title": job_details.role,
            "application_date": get_todays_date(),
            "company_name": recruiter_personal_details.first_name,
            "company_email": recruiter_personal_details.email,
            "website_url": recruiter_details.company_website,
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


def send_payment_receipt(order, name, phone_number, email, order_id, transaction_id):
    try:
        amount = order.amount / 100
        data = render_to_string(
            "email_templates/payment_receipt.html",
            {
                "receipt_number": phone_number,
                "date": get_todays_date(),
                "amount": amount,
                "order_id": order_id,
                "transaction_id": transaction_id,
                "transaction_status": "DONE",
                "name": name,
                "logo_url": JOB_ASSURED_LOGO,
                "website_url": COMPANY_URL,
            },
        )
        # pdf_file = generate_pdf(data)
        recipient_email = email
        subject = SUBJECT
        body = render_to_string(
            "email_templates/payment_success.html",
            {
                "receipt_number": phone_number,
                "date": get_todays_date(),
                "amount": amount,
                "order_id": order_id,
                "transaction_id": transaction_id,
                "transaction_status": "DONE",
                "name": name,
                "logo_url": JOB_ASSURED_LOGO,
                "company_name": COMPANY_NAME,
                "company_email": COMPANY_EMAIL,
                "website_url": COMPANY_URL,
            },
        )
        email = EmailMessage(subject, body, to=[recipient_email])
        email.content_subtype = "html"
        # email.attach("payment_receipt.pdf", pdf_file.read(), "application/pdf")
        email.send()

    except Exception as e:
        raise serializers.ValidationError(
            {"error": f"An error occurred in `payment_receipt`: {str(e)}"}
        )
