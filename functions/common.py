from rest_framework.request import Request
import random

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))
from constants.errors import *
from rest_framework.response import Response
from rest_framework import status


class ResponseHandler:
    @staticmethod
    def success(data=None, status_code=200):
        response_data = {
            "success": True,
            "data": data,
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def error(message=RESPONSE_ERROR, status_code=400):
        response_data = {
            "success": False,
            "message": message,
        }
        return Response(response_data, status=status_code)


def get_login_request_payload(request: Request, key: str, default=None):
    return request.data.get(key, default)


def serializer_handle(Serializers, request):
    serializer = Serializers(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return ResponseHandler.success(
            serializer.data, status_code=status.HTTP_201_CREATED
        )
    return ResponseHandler.error(
        serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
    )


def update_handle(model_class, serializer_class, request):
    instance_id = request.data.get("id")
    try:
        instance = model_class.objects.get(id=instance_id)
    except model_class.DoesNotExist:
        return ResponseHandler.error(
            f"{model_class.__name__} {ERROR_NOT_FOUND}",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    serializer = serializer_class(instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    return ResponseHandler.error(
        serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
    )


def get_handle_profile(model, serializer_class, request):
    try:
        instance = model.objects.get(user=request.user)
        serializer = serializer_class(instance)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except model.DoesNotExist:
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )


def get_handle(model, serializer_class, request):
    instances = model.objects.filter(user=request.id)
    serializer = serializer_class(instances, many=True)
    return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)


def delete_handle(model, request):
    instance_id = request.data.get("id")
    instances = model.objects.filter(id=instance_id)
    if instances.exists():
        instances.delete()
        return ResponseHandler.success(
            {"message": REMOVE_SUCCESS}, status_code=status.HTTP_204_NO_CONTENT
        )
    return ResponseHandler.error(ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)
