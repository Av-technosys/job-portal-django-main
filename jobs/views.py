from django.shortcuts import render
from .serializers import Section1Serializer, Section2Serializer, Section3Serializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Jobs
from handlers.common import request_handler


# Section 1
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def section1_api_view(request):
    return request_handler(Jobs, Section1Serializer, request)


# Section 2
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def section2_api_view(request):
    return request_handler(Jobs, Section2Serializer, request)


# Section 3
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def section3_api_view(request):
    return request_handler(Jobs, Section3Serializer, request)
