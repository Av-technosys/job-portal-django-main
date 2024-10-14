from django.shortcuts import render
from .serializers import (
    JobInfoSerializer,
    JobContactInfoSerializer,
    JobDescriptionSerializer,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import JobInfo, JobContactInfo, JobDescription
from handlers.common import request_handler


# Section 1 (JobDetails)
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_info_api_view(request):
    return request_handler(JobInfo, JobInfoSerializer, request)


# Section 2 (JobContactInfo)
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_contact_info_api_view(request):
    return request_handler(JobContactInfo, JobContactInfoSerializer, request)


# Section 3 (JobDescription)
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_description_api_view(request):
    return request_handler(JobDescription, JobDescriptionSerializer, request)
