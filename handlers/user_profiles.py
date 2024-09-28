from functions.common import *
from constants.errors import *


def request_handler(model, serializer, request):
    match request.method:
        case "GET":
            return get_handle(model, serializer, request)
        case "POST":
            return serializer_handle(serializer, request)
        case "PATCH":
            return update_handle(model, serializer, request)
        case "DELETE":
            return delete_handle(model, request)
        case _:
            return ResponseHandler.error(
                METHOD_ERROR, status_code=status.HTTP_405_METHOD_NOT_ALLOWED
            )
