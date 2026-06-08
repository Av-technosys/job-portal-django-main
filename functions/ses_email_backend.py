import boto3
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class SESEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.client = boto3.client(
            "ses",
            region_name=settings.AWS_SES_REGION_NAME,
            aws_access_key_id=settings.SES_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.SES_AWS_SECRET_ACCESS_KEY,
        )

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sent_count = 0
        for email_message in email_messages:
            try:
                self.client.send_raw_email(
                    Source=email_message.from_email or settings.DEFAULT_FROM_EMAIL,
                    Destinations=email_message.recipients(),
                    RawMessage={"Data": email_message.message().as_bytes()},
                )
                sent_count += 1
            except Exception:
                if not self.fail_silently:
                    raise

        return sent_count
