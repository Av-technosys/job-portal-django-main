from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from functions.common import handle_serializer
from constants.errors import *
from .serializers import *


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def student_profile(request):
    serializer = StudentProfileSerializer(data=request.data)
    return handle_serializer(serializer)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def academic_qualification(request):
    serializer = AcademicQualificationSerializer(data=request.data)
    return handle_serializer(serializer)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def work_experience(request):
    serializer = WorkExperienceSerializer(data=request.data)
    return handle_serializer(serializer)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def skill_set(request):
    serializer = SkillSetSerializer(data=request.data)
    return handle_serializer(serializer)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def projects(request):
    serializer = ProjectsSerializer(data=request.data)
    return handle_serializer(serializer)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def certifications(request):
    serializer = CertificationsSerializer(data=request.data)
    return handle_serializer(serializer)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def social_urls(request):
    serializer = SocialUrlsSerializer(data=request.data)
    return handle_serializer(serializer)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_student_profile(request):
    request.user = 2
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return Response({"error": ERROR_USER_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    serializer = StudentProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_academic_qualification(request):
    request.user = 2

    qualification = AcademicQualification.objects.filter(user=request.user)
    serializer = AcademicQualificationSerializer(qualification, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_work_experience(request):
    request.user = 2
    experiences = WorkExperience.objects.filter(user=request.user)
    serializer = WorkExperienceSerializer(experiences, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_skill_set(request):
    request.user = 2
    skills = SkillSet.objects.filter(user=request.user)
    serializer = SkillSetSerializer(skills, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_projects(request):
    request.user = 2
    print(request)
    projects = Projects.objects.filter(user=request.user)
    serializer = ProjectsSerializer(projects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_certifications(request):
    request.user = 2
    certifications = Certifications.objects.filter(user=request.user)
    serializer = CertificationsSerializer(certifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_social_urls(request):
    request.user = 2
    urls = SocialUrls.objects.filter(user=request.user)
    serializer = SocialUrlsSerializer(urls, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)