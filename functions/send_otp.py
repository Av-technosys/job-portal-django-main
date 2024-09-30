from rest_framework import serializers
from constants.env_data import (
    TWILIO_ACCOUNT_SID,
    TWILIO_PHONE_NUMBER,
    TWILIO_AUTH_TOKEN,
)
from twilio.rest import Client
from constants.errors import (
    FAILED_SEND_OTP,
)
from constants.accounts import (
    OTP_MESSAGE,
)


def send_phone_otp(self, phone_number, otp):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=f"{OTP_MESSAGE} {otp}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number,
        )
    except Exception as e:
        raise serializers.ValidationError({"error": FAILED_SEND_OTP.format(e)})
