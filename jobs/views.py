from django.shortcuts import render
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from functions.common import get_data_from_id_and_serialize
from handlers.common import (
    request_handler,
    filter_search_handler,
    job_apply_handler,
    job_application_handler,
)
from user_profiles.models import StudentProfile
from user_profiles.serializers import StudentProfileSerializer


# Section 1: JobDetails
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_details_api_view(request):
    return request_handler(JobInfo, JobDetailsSerializer, request)


# Section 2: JobDescription
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_description_api_view(request):
    return request_handler(JobDescription, JobDescriptionSerializer, request)


# Section 2: ContactAndSkills
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def contact_and_skills_api_view(request):
    return request_handler(ContactAndSkills, ContactAndSkillsSerializer, request)


# Section 3: JobOverviewAndQualifications
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_overview_and_qualifications_api_view(request):
    return request_handler(
        JobOverviewAndQualifications, JobOverviewAndQualificationsSerializer, request
    )


# Section 3: SkillsCertificationsResponsibilities
@api_view(["POST", "GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def skills_certifications_responsibilities_api_view(request):
    return request_handler(
        SkillsCertificationsResponsibilities,
        SkillsCertificationsResponsibilitiesSerializer,
        request,
    )


# Combined View for JobDetails
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getJobDetails(request):
    job_id = request.data.get("job_id")
    return get_data_from_id_and_serialize(
        JobDetails, CombinedJobDetailsSerializer, job_id
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_job(request):
    return job_apply_handler(JobApplySerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    return filter_search_handler(JobInfo, JobDetailsSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def submitted_jobs_application(request):
    return job_application_handler(
        JobApply, JobApplySerializer, StudentProfile, StudentProfileSerializer, request
    )
