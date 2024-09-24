from rest_framework.request import Request
from rest_framework import status
from rest_framework.response import Response
from constants.errors import * 

def get_login_request_payload(request: Request, key: str, default=None):
    return request.data.get(key, default)

def handle_serializer(serializer):
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def update_handle(model_class, serializer_class, request):
    instance_id = request.data.get('id')
    try:
        instance = model_class.objects.get(id=instance_id)
    except model_class.DoesNotExist:
        return Response({"error": f"{model_class.__name__} {ERROR_NOT_FOUND}"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializer_class(instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
