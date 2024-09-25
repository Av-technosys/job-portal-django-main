from rest_framework.decorators import api_view, permission_classes
from functions.common import *
from .serializers import *


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
def student_profile(request):
    if request.method == 'GET':
        return get_handle_profile(StudentProfile, StudentProfileSerializer, request)
    
    elif request.method == 'POST':
        return serializer_handle(StudentProfileSerializer, request)
    
    elif request.method == 'PATCH':
        return update_handle(StudentProfile, StudentProfileSerializer, request)

    elif request.method == 'DELETE':
        return delete_handle(StudentProfile, request)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
def academic_qualification(request):
    if request.method == 'GET':
        return get_handle(AcademicQualification, AcademicQualificationSerializer, request)
    
    elif request.method == 'POST':
        return serializer_handle(AcademicQualificationSerializer, request)

    elif request.method == 'PATCH':
        return update_handle(AcademicQualification, AcademicQualificationSerializer, request)

    elif request.method == 'DELETE':
        return delete_handle(AcademicQualification, request)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
def work_experience(request):
    if request.method == 'GET':
        return get_handle(WorkExperience, WorkExperienceSerializer, request)
    
    elif request.method == 'POST':
        return serializer_handle(WorkExperienceSerializer, request)

    elif request.method == 'PATCH':
        return update_handle(WorkExperience, WorkExperienceSerializer, request)

    elif request.method == 'DELETE':
        return delete_handle(WorkExperience, request)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
def skill_set(request):
    if request.method == 'GET':
        return get_handle(SkillSet, SkillSetSerializer, request)

    elif request.method == 'POST':
        return serializer_handle(SkillSetSerializer, request)

    elif request.method == 'PATCH':
        return update_handle(SkillSet, SkillSetSerializer, request)

    elif request.method == 'DELETE':
        return delete_handle(SkillSet, request)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
def projects(request):
    if request.method == 'GET':
        return get_handle(Projects, ProjectsSerializer, request)
    
    elif request.method == 'POST':
        return serializer_handle(ProjectsSerializer, request)

    elif request.method == 'PATCH':
        return update_handle(Projects, ProjectsSerializer, request)

    elif request.method == 'DELETE':
        return delete_handle(Projects, request)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
def certifications(request):
    if request.method == 'GET':
        return get_handle(Certifications, CertificationsSerializer, request)

    elif request.method == 'POST':
        return serializer_handle(CertificationsSerializer, request)

    elif request.method == 'PATCH':
        return update_handle(Certifications, CertificationsSerializer, request)

    elif request.method == 'DELETE':
        return delete_handle(Certifications, request)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
# @permission_classes([IsAuthenticated])
def social_urls(request):
    if request.method == 'GET':
        return get_handle(SocialUrls, SocialUrlsSerializer, request)

    elif request.method == 'POST':
        return serializer_handle(SocialUrlsSerializer, request)

    elif request.method == 'PATCH':
        return update_handle(SocialUrls, SocialUrlsSerializer, request)

    elif request.method == 'DELETE':
        return delete_handle(SocialUrls, request)
