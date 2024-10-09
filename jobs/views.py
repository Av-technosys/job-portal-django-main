from django.shortcuts import render
from functions.common import serializer_handle
from .serializers import Section1Serializer, Section2Serializer, Section3Serializer
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated

# Section 1 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def section1_api_view(request):
    return serializer_handle(Section1Serializer, request)

# Section 2 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def section2_api_view(request):
    return serializer_handle(Section2Serializer, request)

# Section 3 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def section3_api_view(request):
    return serializer_handle(Section3Serializer, request)
