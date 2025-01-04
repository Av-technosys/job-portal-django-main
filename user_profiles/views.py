from rest_framework.decorators import api_view, permission_classes
from functions.common import *
from user_profiles.models import *
from accounts.models import User
from .serializers import *
from handlers.common import request_handler
from rest_framework.permissions import IsAuthenticated
from handlers.permissions import IsRecruiter, IsJobSeeker
from jobs.models import JobApply
from jobs.serializers import JobApplySerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def job_seeker_personal_details(request):
    if request.method == "GET":
        return get_customize_handler(
            User, JobSeekerPersonalProfileSerializer, {"email": request.user}
        )
    return request_handler(StudentProfile, JobSeekerPersonalProfileSerializer, request)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def job_seeker_general_details(request):
    if request.method == "GET":
        return get_handle_profile(
            AcademicQualification, JobSeekerGeneralProfileSerializer, request
        )
    else:
        return request_handler(
            AcademicQualification, JobSeekerGeneralProfileSerializer, request
        )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def job_seeker_additional_details(request):
    if request.method == "GET":
        return get_customize_handler(
            User, JobSeekerAdditionalProfileSerializer, {"email": request.user}
        )
    else:
        return request_handler(
            WorkExperience, JobSeekerAdditionalProfileSerializer, request
        )


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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def company_profile(request):
    if request.method == "GET":
        return get_customize_handler(
            User, RecruiterProfileSerializer, {"email": request.user}
        )
    else:
        return request_handler(OrganizationInfo, RecruiterProfileSerializer, request)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def recruiter_founding_info_details(request):
    if request.method == "GET":
        return get_customize_handler(
            User, RecruiterProfileFoundingInfoSerializer, {"email": request.user}
        )
    else:
        return request_handler(
            FoundingInfo, RecruiterProfileFoundingInfoSerializer, request
        )


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def job_details(request):
    return request_handler(FoundingInfo, FoundingInfoSerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsRecruiter])
def upload_recruiters(request):
    return request_handler(
        RecruiterUploadedFile, UploadedFileRecruiterSerializer, request
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsRecruiter])
def social_links_recruiter(request):
    if request.method == "GET":
        return request_handler(
            SocialMediaLinkRecruiter, SocialLinkItemSerializer, request
        )
    return request_handler(
        SocialMediaLinkRecruiter, SocialLinksRecruiterSerializer, request
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def social_links_job_seeker(request):
    if request.method == "GET":
        return request_handler(
            SocialMediaLinkJobSeeker, SocialLinkItemJSSerializer, request
        )
    return request_handler(
        SocialMediaLinkJobSeeker, SocialLinksJobSeekerSerializer, request
    )


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def salary(request):
    return request_handler(Salary, SalarySerializer, request)


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsRecruiter])
def file_upload_recruiter(request):
    return upload_handler(
        RecruiterUploadedFile, UploadedFileRecruiterSerializer, request
    )


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def file_upload_job_seeker(request):
    return upload_handler(
        JobSeekerUploadedFile, UploadedFileJobSeekerSerializer, request
    )


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
    return filter_search_handler(OrganizationInfo, FindRecruiterListSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recruiter_details(request, recruiter_id):
    return get_data_from_id_and_serialize(
        OrganizationInfo, CombinedCompanyDetailSerializer, recruiter_id
    )
