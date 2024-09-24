from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from functions.common import handle_serializer, update_handle
from constants.errors import *
from .serializers import *


@api_view(['GET', 'POST', 'PATCH'])
# @permission_classes([IsAuthenticated])
def student_profile(request):
    if request.method == 'GET':
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response({"error": ERROR_USER_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = StudentProfileSerializer(data=request.data)
        return handle_serializer(serializer)
    
    elif request.method == 'PATCH':
        return update_handle(StudentProfile, StudentProfileSerializer, request)


@api_view(['GET', 'POST', 'PATCH'])
# @permission_classes([IsAuthenticated])
def academic_qualification(request):
    if request.method == 'GET':
        qualification = AcademicQualification.objects.filter(user=request.user)
        serializer = AcademicQualificationSerializer(qualification, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = AcademicQualificationSerializer(data=request.data)
        return handle_serializer(serializer)

    elif request.method == 'PATCH':
        return update_handle(AcademicQualification, AcademicQualificationSerializer, request)


@api_view(['GET', 'POST', 'PATCH'])
# @permission_classes([IsAuthenticated])
def work_experience(request):
    if request.method == 'GET':
        experiences = WorkExperience.objects.filter(user=request.user)
        serializer = WorkExperienceSerializer(experiences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = WorkExperienceSerializer(data=request.data)
        return handle_serializer(serializer)

    elif request.method == 'PATCH':
        return update_handle(WorkExperience, WorkExperienceSerializer, request)


@api_view(['GET', 'POST', 'PATCH'])
# @permission_classes([IsAuthenticated])
def skill_set(request):
    if request.method == 'GET':
        skills = SkillSet.objects.filter(user=request.user)
        serializer = SkillSetSerializer(skills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SkillSetSerializer(data=request.data)
        return handle_serializer(serializer)

    elif request.method == 'PATCH':
        return update_handle(SkillSet, SkillSetSerializer, request)


@api_view(['GET', 'POST', 'PATCH'])
# @permission_classes([IsAuthenticated])
def projects(request):
    if request.method == 'GET':
        projects = Projects.objects.filter(user=request.user)
        serializer = ProjectsSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ProjectsSerializer(data=request.data)
        return handle_serializer(serializer)

    elif request.method == 'PATCH':
        return update_handle(Projects, ProjectsSerializer, request)


@api_view(['GET', 'POST', 'PATCH'])
# @permission_classes([IsAuthenticated])
def certifications(request):
    if request.method == 'GET':
        certifications = Certifications.objects.filter(user=request.user)
        serializer = CertificationsSerializer(certifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = CertificationsSerializer(data=request.data)
        return handle_serializer(serializer)

    elif request.method == 'PATCH':
        return update_handle(Certifications, CertificationsSerializer, request)


@api_view(['GET', 'POST', 'PATCH'])
# @permission_classes([IsAuthenticated])
def social_urls(request):
    if request.method == 'GET':
        urls = SocialUrls.objects.filter(user=request.user)
        serializer = SocialUrlsSerializer(urls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SocialUrlsSerializer(data=request.data)
        return handle_serializer(serializer)

    elif request.method == 'PATCH':
        return update_handle(SocialUrls, SocialUrlsSerializer, request)
