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
def get_job_details(request):
    job_id = request.data.get("job_id")
    return get_data_from_id_and_serialize(JobInfo, CombinedJobDetailsSerializer, job_id)


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
    return filter_search_handler(JobInfo, JobDetailsSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def submitted_jobs_application(request):
    return application_handler(
        JobApply,
        JobApplySerializer,
        StudentProfile,
        StudentProfileSerializer,
        StudentProfile,
        request,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_submitted_jobs(request):
    return application_handler(
        JobApply,
        JobApplySerializer,
        JobInfo,
        JobDetailsSerializer,
        StudentProfile,
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
@permission_classes([IsAuthenticated, IsJobSeeker])
def applied_saved_jobs(request):
    return jobs_profiles_counter_handler(JobSaved, JobApply, request) 

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def posted_saved_profile(request):
    return jobs_profiles_counter_handler(JobSaved, JobInfo, request) 
   
