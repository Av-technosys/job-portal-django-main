# profiles/serializers.py
from rest_framework import serializers
from accounts.models import User
from constants.errors import RESPONSE_ERROR
from functions.common import ResponseHandler
from constants.fcm import FCM_TOKEN_STORED
from .models import *


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = "__all__"


class AcademicQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicQualification
        fields = "__all__"


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = "__all__"


class SkillSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillSet
        fields = "__all__"


class CertificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = "__all__"


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = "__all__"


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = "__all__"


class OrganizationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInfo
        fields = "__all__"


class FoundingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundingInfo
        fields = "__all__"


class UploadedFileRecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterUploadedFile
        fields = "__all__"


class UploadedFileJobSeekerSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerUploadedFile
        fields = "__all__"

    def create(self, validated_data):
        uploaded_file = JobSeekerUploadedFile(**validated_data)
        uploaded_file.save()
        return uploaded_file


class CombineStudentProfileSerializer(serializers.ModelSerializer):
    academic_qualifications = AcademicQualificationSerializer(
        many=True, read_only=True, source="user.aq_fk_user"
    )
    work_experiences = WorkExperienceSerializer(
        many=True, read_only=True, source="user.we_fk_user"
    )
    skill_sets = SkillSetSerializer(many=True, read_only=True, source="user.ss_fk_user")
    certifications = CertificationsSerializer(
        many=True, read_only=True, source="user.ces_fk_user"
    )
    projects = ProjectsSerializer(many=True, read_only=True, source="user.ps_fk_user")
    salary = SalarySerializer(many=True, read_only=True, source="user.sy_fk_user")
    uploaded_files = UploadedFileJobSeekerSerializer(
        many=True, read_only=True, source="user.social_media_links_job_seeker"
    )

    class Meta:
        model = StudentProfile
        fields = STUDENT_PROFILE_COMBINED_FIELDS


class StoreFCMTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField()

    def return_response(self, validated_data):
        user_id = self.initial_data.get("user")
        if user_id:
            user = User.objects.get(id=user_id)
            fcm_token_instance = FCMToken.objects.update_or_create(
                user=user, defaults={"fcm_token": validated_data["fcm_token"]}
            )

            if fcm_token_instance:
                return {"message": FCM_TOKEN_STORED}

        raise ResponseHandler.api_exception_error(RESPONSE_ERROR)


class CombinedCompanyDetailSerializer(serializers.ModelSerializer):
    founding_info = FoundingInfoSerializer(
        many=False, read_only=True, source="user.founding_info"
    )

    class Meta:
        model = OrganizationInfo
        fields = COMPANY_PROFILE_FIELDS


class ListCandidateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = LIST_CANDIDATE_FEILDS


class SocialLinksRecruiterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialMediaLinkRecruiter
        fields = "__all__"


class SocialLinksJobSeekerSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialMediaLinkJobSeeker
        fields = "__all__"
