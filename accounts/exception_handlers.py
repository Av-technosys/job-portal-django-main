from rest_framework.views import exception_handler

from constants.errors import ERROR_USER_INACTIVE


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    detail = response.data.get("detail") if response is not None else None
    if (
        response is not None
        and detail is not None
        and ERROR_USER_INACTIVE in str(detail)
    ):
        response.data = {
            "success": False,
            "message": ERROR_USER_INACTIVE,
            "force_logout": True,
        }
    return response
