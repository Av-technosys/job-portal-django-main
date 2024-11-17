# profiles/serializers.py
from rest_framework import serializers
from .models import *


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = "__all__"

    def create(self, validated_data):
        student = StudentProfile(**validated_data)
        student.save()
        return student


class AcademicQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicQualification
        fields = "__all__"

    def create(self, validated_data):
        academic_qualification = AcademicQualification(**validated_data)
        academic_qualification.save()
        return academic_qualification


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = "__all__"

    def create(self, validated_data):
        work_experience = WorkExperience(**validated_data)
        work_experience.save()
        return work_experience


class SkillSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillSet
        fields = "__all__"

    def create(self, validated_data):
        skill_set = SkillSet(**validated_data)
        skill_set.save()
        return skill_set


class CertificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = "__all__"

    def create(self, validated_data):
        certification = Certifications(**validated_data)
        certification.save()
        return certification


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = "__all__"

    def create(self, validated_data):
        project = Projects(**validated_data)
        project.save()
        return project


class SocialUrlsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialUrls
        fields = "__all__"

    def create(self, validated_data):
        social_url = SocialUrls(**validated_data)
        social_url.save()
        return social_url


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = "__all__"

    def create(self, validated_data):
        company_profile = CompanyProfile(**validated_data)
        company_profile.save()
        return company_profile


class JobDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDetails
        fields = "__all__"

    def create(self, validated_data):
        job_details = JobDetails(**validated_data)
        job_details.save()
        return job_details


class CompanyIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyId
        fields = "__all__"

    def create(self, validated_data):
        company_id = CompanyId(**validated_data)
        company_id.save()
        return company_id


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = "__all__"

    def create(self, validated_data):
        uploaded_file = UploadedFile(**validated_data)
        uploaded_file.save()
        return uploaded_file


class CombinedUserProfileSerializer(serializers.ModelSerializer):
    academic_qualifications = AcademicQualificationSerializer(many=True, read_only=True)
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    skill_sets = SkillSetSerializer(many=True, read_only=True)
    certifications = CertificationsSerializer(many=True, read_only=True)
    projects = ProjectsSerializer(many=True, read_only=True)
    social_urls = SocialUrlsSerializer(many=True, read_only=True)
    company_profile = CompanyProfileSerializer(read_only=True)
    job_details = JobDetailsSerializer(read_only=True)
    company_id = CompanyIdSerializer(read_only=True)
    uploaded_files = UploadedFileSerializer(many=True, read_only=True)

    class Meta:
        model = StudentProfile
        fields = JOB_DETAILS_FIELDS
