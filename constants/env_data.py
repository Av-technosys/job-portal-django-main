import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_bool_env(key, default=False):
    value = os.getenv(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def get_int_env(key, default):
    value = os.getenv(key)
    if value in (None, ""):
        return default
    return int(value)

# TWILIO
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# AUTH
USER_POOL_ID = os.getenv("USER_POOL_ID")
AUTH_SECRET = os.getenv("AUTH_SECRET")

# AWS SES EMAIL
AWS_SES_REGION_NAME = os.getenv("AWS_SES_REGION_NAME", "ap-south-1")
SES_AWS_ACCESS_KEY_ID = os.getenv("SES_AWS_ACCESS_KEY_ID")
SES_AWS_SECRET_ACCESS_KEY = os.getenv("SES_AWS_SECRET_ACCESS_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
AWS_SES_SMTP_USERNAME = os.getenv("AWS_SES_SMTP_USERNAME")
AWS_SES_SMTP_PASSWORD = os.getenv("AWS_SES_SMTP_PASSWORD")
AWS_SES_FROM_EMAIL = os.getenv("AWS_SES_FROM_EMAIL")

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "functions.ses_email_backend.SESEmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", f"email-smtp.{AWS_SES_REGION_NAME}.amazonaws.com")
EMAIL_USE_TLS = get_bool_env("EMAIL_USE_TLS", True)
EMAIL_PORT = get_int_env("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER") or AWS_SES_SMTP_USERNAME
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") or AWS_SES_SMTP_PASSWORD
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL") or EMAIL_FROM or AWS_SES_FROM_EMAIL

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_FILE_OVERWRITE = os.getenv("AWS_S3_FILE_OVERWRITE")
AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# RAZORPAY
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
