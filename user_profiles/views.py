from rest_framework.decorators import api_view, permission_classes
from functions.common import *
from .serializers import *
from handlers.common import request_handler
from rest_framework.permissions import IsAuthenticated
from handlers.permissions import IsRecruiter, IsJobSeeker
from jobs.models import JobApply
from jobs.serializers import JobApplySerializer


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def student_profile(request):
    if request.method == "GET":
        return get_handle_profile(StudentProfile, StudentProfileSerializer, request)
    else:
        return request_handler(StudentProfile, StudentProfileSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def academic_qualification(request):
    return request_handler(
        AcademicQualification, AcademicQualificationSerializer, request
    )


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def work_experience(request):
    return request_handler(WorkExperience, WorkExperienceSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def skill_set(request):
    return request_handler(SkillSet, SkillSetSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def projects(request):
    return request_handler(Projects, ProjectsSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def certifications(request):
    return request_handler(Certifications, CertificationsSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def social_urls(request):
    return request_handler(SocialUrls, SocialUrlsSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def company_profile(request):
    if request.method == "GET":
        return get_handle_profile(OrganizationInfo, OrganizationInfoSerializer, request)
    else:
        return request_handler(OrganizationInfo, OrganizationInfoSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_details(request):
    return request_handler(FoundingInfo, FoundingInfoSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsRecruiter])
def file_upload_recruiter(request):
    return upload_handler(
        RecruiterUploadedFile, UploadedFileRecruiterSerializer, request
    )


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def file_upload_job_seeker(request):
    return upload_handler(JobSeekerUploadedFile, UploadedFileSeekerSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_seeker(request):
    return filter_search_handler(StudentProfile, StudentProfileSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def students_all_details(request):
    student_id = request.data.get("student_id")
    return get_data_from_id_and_serialize(
        StudentProfile, CombineStudentProfileSerializer, student_id
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def application_status(request):
    return handle_application_status(JobApply, JobApplySerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def store_fcm_token(request):
    return serializer_handle_customize_response_only_validate(
        StoreFCMTokenSerializer, request
    )


@api_view(["GET"])
def get_recruiter(request):
    return filter_search_handler(OrganizationInfo, OrganizationInfoSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recruiter_details(request, recruiter_id):
    return get_data_from_id_and_serialize(
        OrganizationInfo, CombinedCompanyDetailSerializer, recruiter_id
    )
