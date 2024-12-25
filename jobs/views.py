from django.shortcuts import render
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from functions.common import get_data_from_id_and_serialize
from handlers.common import *
from user_profiles.models import StudentProfile
from user_profiles.serializers import StudentProfileSerializer
from handlers.permissions import IsRecruiter, IsJobSeeker
from accounts.models import CandidateSaved


# Section 1: JobDetails
@api_view(["GET","POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_details_api_view(request):
    return request_handler(JobInfo, JobCombinedSerializer, request)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_job(request):
    return job_apply_handler(JobApplySerializer, JobInfo, request)


@api_view(["GET"])
def list_jobs(request):
    return filter_search_handler(JobInfo, JobListingSeekerViewSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_posted_jobs(request):
    request.data["owner"] = [request.user.id]
    return filter_search_handler(JobInfo, JobPostedListSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def submitted_jobs_application(request):
    return application_handler(
        JobApply,
        JobApplySerializer,
        StudentProfile,
        StudentProfileSerializer,
        request,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_submitted_jobs(request):
    return application_handler(
        JobApply,
        JobApplySerializer,
        JobInfo,
        AppliedJobListViewSerializer,
        request,
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated, IsRecruiter])
def application_status(request):
    return handle_application_status(JobApply, JobApplySerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def chat(request, application_id):
    return message_handler(CommunicationSerializer, request, application_id)


@api_view(["POST", "DELETE", "GET"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def save_job(request):
    return job_save_handler(
        JobSaveSerializer, JobListingSeekerViewSerializer, JobSaved, JobInfo, request
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summary_view(request):
    return summary_counter_handler(JobApply, JobSaved, CandidateSaved, JobInfo, request)
