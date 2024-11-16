from rest_framework.decorators import api_view, permission_classes
from functions.common import *
from .serializers import *
from handlers.common import request_handler
from rest_framework.permissions import IsAuthenticated
from handlers.permissions import IsRecruiter, IsJobSeeker


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
        return get_handle_profile(CompanyProfile, CompanyProfileSerializer, request)
    else:
        return request_handler(CompanyProfile, CompanyProfileSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_details(request):
    return request_handler(JobDetails, JobDetailsSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def company_id(request):
    return request_handler(CompanyId, CompanyIdSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def file_upload(request):
    return upload_handler(UploadedFile, UploadedFileSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_seeker(request):
    return filter_search_handler(StudentProfile, StudentProfileSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def get_all_students_detail(request):
    student_id = request.data.get("student_id")
    return get_data_from_id_and_serialize(StudentProfile, CombinedUserProfileSerializer, student_id)