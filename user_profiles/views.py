from rest_framework.decorators import api_view, permission_classes
from functions.common import *
from .serializers import *
from handlers.user_profiles import *
from rest_framework.permissions import IsAuthenticated


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
