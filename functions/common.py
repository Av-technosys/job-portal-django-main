from rest_framework.request import Request
from rest_framework import status
from rest_framework.response import Response

def get_login_request_payload(request: Request, key: str, default=None):
    return request.data.get(key, default)

def handle_serializer(serializer):
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    