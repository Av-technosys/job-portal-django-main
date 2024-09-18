from rest_framework.request import Request

def get_login_request_payload(request: Request, key: str, default=None):
    return request.data.get(key, default)