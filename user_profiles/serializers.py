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


class JobSeekerPersonalProfileSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.CharField(source="sp_fk_user.date_of_birth")
    gender = serializers.IntegerField(source="sp_fk_user.gender")
    address_line_1 = serializers.CharField(source="sp_fk_user.address_line_1")
    address_line_2 = serializers.CharField(source="sp_fk_user.address_line_2")
    city = serializers.CharField(source="sp_fk_user.city")
    state = serializers.CharField(source="sp_fk_user.state")
    country = serializers.CharField(source="sp_fk_user.country")
    postal_code = serializers.IntegerField(source="sp_fk_user.postal_code")
    student_profile_id = serializers.IntegerField(
        source="sp_fk_user.id", required=False
    )

    class Meta:
        model = User
        fields = JOB_SEEKER_PROFILE_PERSONAL_INFO

    def create(self, validated_data):
        user = self.context["request"].user

        user_info_data = {}
        for key in JOB_SEEKER_PROFILE_PERSONAL_INFO_SUB_KEYS_1:
            if validated_data[key] is not None:
                user_info_data[key] = validated_data[key]

        User.objects.filter(pk=user.id).update(**user_info_data)
        user_sp_info_data = {
            "user": user,
        }
        validated_sp_data = validated_data["sp_fk_user"]
        for key in JOB_SEEKER_PROFILE_PERSONAL_INFO_SUB_KEYS_2:
            if validated_sp_data[key] is not None:
                user_sp_info_data[key] = validated_sp_data[key]
        sp_lookup = {
            "user": user.id,
        }
        if "id" in validated_sp_data and validated_sp_data["id"] is not None:
            sp_lookup["id"] = validated_sp_data["id"]
        StudentProfile.objects.update_or_create(
            **sp_lookup,
            defaults=user_sp_info_data,
        )

        return validated_data


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
