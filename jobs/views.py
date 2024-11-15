from django.shortcuts import render
from .serializers import (
    JobInfoSerializer,
    JobContactInfoSerializer,
    JobDescriptionSerializer,
    CombinedJobDetailsSerializer,
    JobApplySerializer,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import JobInfo, JobContactInfo, JobDescription, JobApply
from functions.common import get_data_from_id_and_serialize
from handlers.common import (
    request_handler,
    filter_search_handler,
    job_apply_handler,
    application_handler,
)
from user_profiles.models import StudentProfile
from user_profiles.serializers import StudentProfileSerializer


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_job_details(request):
    job_id = request.data.get("job_id")
    return get_data_from_id_and_serialize(JobInfo, CombinedJobDetailsSerializer, job_id)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_job(request):
    return job_apply_handler(JobApplySerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    return filter_search_handler(JobInfo, JobInfoSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def submitted_jobs_application(request):
    return application_handler(
        JobApply, JobApplySerializer, StudentProfile, StudentProfileSerializer, request
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_submetted_jobs(request):
    return application_handler(
        JobApply, JobApplySerializer, JobInfo, JobInfoSerializer, request
    )
