from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from handlers.common import *
from user_profiles.models import StudentProfile
from user_profiles.serializers import ListCandidateSerializer, StudentProfileSerializer
from handlers.permissions import IsRecruiter, IsJobSeeker


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsRecruiter])
def job_details_api_view(request):
    return request_handler(JobInfo, JobCombinedSerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def apply_job(request):
    return job_apply_handler(JobApplySerializer, JobInfo, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    return filter_search_handler(JobInfo, JobSeekerListingViewSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsRecruiter])
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


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsRecruiter])
def application_status(request):
    return handle_application_status(JobApply, JobApplySerializer, request)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def chat(request, application_id):
    return message_handler(CommunicationSerializer, request, application_id)


@api_view(["POST", "DELETE", "GET"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def save_job(request):
    return job_save_handler(
        JobSaveSerializer,
        SavedJobsJobSeekerListingViewSerializer,
        JobSaved,
        JobInfo,
        request,
    )


@api_view(["POST", "DELETE", "GET"])
@permission_classes([IsAuthenticated, IsRecruiter])
def save_cadidate(request):
    return candidate_save_handler(
        CandidateSaveSerializer,
        ListCandidateSerializer,
        CandidateSaved,
        StudentProfile,
        request,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summary_view(request):
    return summary_counter_handler(JobApply, JobSaved, CandidateSaved, JobInfo, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_details_by_id(request, job_id):
    return job_details_by_job_id(JobInfo, job_id, JobDetailsCombinedSerializer, request)


@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated, IsRecruiter])
def job_status_by_recruiter(request):
    return job_status_update(JobInfo, JobStatusUpdateSerializer, request)
