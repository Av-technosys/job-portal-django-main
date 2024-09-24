# profiles/serializers.py
from rest_framework import serializers
from .models import *
from constants.student_profiles import * 


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = STUDENT_PROFILE_META_FIELDS
    def create(self, validated_data):
        student = StudentProfile(**validated_data)
        student.save()
        return student
    
class AcademicQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicQualification
        fields = ACADEMIC_QUALIFICATIONE_META_FIELDS
    def create(self, validated_data):
        academic_qualification = AcademicQualification(**validated_data)
        academic_qualification.save()
        return academic_qualification


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = WORK_EXPERIENCEE_META_FIELDS
    def create(self, validated_data):
        work_experience = WorkExperience(**validated_data)
        work_experience.save()
        return work_experience


class SkillSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillSet
        fields = SKILL_SETE_META_FIELDS
    def create(self, validated_data):
        skill_set = SkillSet(**validated_data)
        skill_set.save()
        return skill_set


class CertificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = CERTIFICATIONSE_META_FIELDS
    def create(self, validated_data):
        certification = Certifications(**validated_data)
        certification.save()
        return certification


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = PROJECTE_META_FIELDS
    def create(self, validated_data):
        project = Projects(**validated_data)
        project.save()
        return project

class SocialUrlsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialUrls
        fields = SOCIALE_META_FIELDS
    def create(self, validated_data):
        SocialUrl = SocialUrls(**validated_data)
        SocialUrl.save()
        return SocialUrl