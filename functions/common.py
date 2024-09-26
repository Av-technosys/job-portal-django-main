from rest_framework.request import Request
import random

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def get_login_request_payload(request: Request, key: str, default=None):
    return request.data.get(key, default)