from rest_framework.request import Request
import random
from rest_framework import status
from rest_framework.exceptions import APIException
from django.contrib.auth import get_user_model
User = get_user_model()  

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


from constants.errors import *
from rest_framework.response import Response
from rest_framework import status


def get_flattened_error_message(message):
    return next(iter(message.values()))[0]


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
            "message": get_flattened_error_message(message),
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def api_exception_error(message=RESPONSE_ERROR):
        return APIException({"message": message, "success": False})


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


def serializer_handle_customize_response_only_validate(Serializers, request):
    serializer = Serializers(data=request.data)
    if serializer.is_valid():
        responseData = serializer.return_response(serializer.data)
        return ResponseHandler.success(
            responseData, status_code=status.HTTP_201_CREATED
        )
    return ResponseHandler.error(
        serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
    )


def serializer_handle_customize_response(Serializers, request):
    serializer = Serializers(data=request.data)
    if serializer.is_valid():
        responseData = serializer.save()
        return ResponseHandler.success(
            responseData, status_code=status.HTTP_201_CREATED
        )
    return ResponseHandler.error(
        serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
    )


def update_handle(model_class, serializer_class, request):
    try:
        instance = model_class.objects.get(id=request.id)
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
        instance = model.objects.get(id=request.id)
        serializer = serializer_class(instance)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except model.DoesNotExist:
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )


def get_handle(model, serializer_class, request):
    instances = model.objects.filter(id=request.id)
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


def upload_handler(model, serializer_class, request):
    if request.method == "GET":
        documents = model.objects.all()
        serializer = serializer_class(documents, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = request.data.copy()
        user = User.objects.get(id=29)
        data['user'] = user.id 
        serializer = serializer_class(data=data)
        
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
