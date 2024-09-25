from rest_framework.request import Request
from rest_framework import status
from rest_framework.response import Response
from constants.errors import * 

def get_login_request_payload(request: Request, key: str, default=None):
    return request.data.get(key, default)

def serializer_handle(Serializers, request):
    serializer = Serializers(data=request.data)
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


def get_handle_profile(model, serializer_class, request):
    try:
        instance = model.objects.get(user=request.user)
        serializer = serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except model.DoesNotExist:
        return Response({"error": ERROR_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)


def get_handle(model, serializer_class, request):
    request.user = 2
    instances = model.objects.filter(user=request.user)
    serializer = serializer_class(instances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def delete_handle(model, request):
    instance_id = request.data.get('id')
    instances = model.objects.filter(id=instance_id)
    if instances.exists():
        instances.delete()
        return Response({"message" : "data removed"}, status=status.HTTP_204_NO_CONTENT)
    return Response({"error": ERROR_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)