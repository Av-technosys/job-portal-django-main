# profiles/serializers.py
from rest_framework import serializers
from accounts.models import User
from constants.errors import ATLEAST_ONE_SKILL_REQUIRED, RESPONSE_ERROR
from functions.common import get_job_seeker_documents, ResponseHandler
from constants.fcm import FCM_TOKEN_STORED
from constants.user_profiles import JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_2
from functions.profile import process_items
from .models import *
from functions.common import get_recruiter_profile_image, get_location_formatted
from django.db import transaction


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

        with transaction.atomic():
            User.objects.filter(pk=user.id).update(**user_info_data)

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


class FindRecruiterListSerializer(serializers.ModelSerializer):
    company_profile_image = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField(source="user.first_name")
    organization_type = serializers.CharField(
        source="user.founding_info.organization_type"
    )
    industry_type = serializers.CharField(source="user.founding_info.industry_type")
    created_date = serializers.DateTimeField()
    updated_date = serializers.DateTimeField()
    company_id = serializers.IntegerField(source="id")
    user = serializers.IntegerField(source="user.id")

    class Meta:
        model = OrganizationInfo
        fields = FIND_RECUITER_VIEW_FEILDS

    def get_company_profile_image(self, obj):
        return get_recruiter_profile_image(obj.user)

    def get_company_name(self, obj):
        return obj.user.first_name

    def get_location(self, obj):
        return get_location_formatted(obj)


class WorkExperienceJobSeekerProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    organization_name = serializers.CharField()
    designation = serializers.CharField()
    experience = serializers.IntegerField()
    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=None,
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)

    class Meta:
        model = WorkExperience
        fields = JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1


class CertificationsJobSeekerProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    certification_name = serializers.CharField()
    institution_name = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)

    class Meta:
        model = Certifications
        fields = JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_2


class ProjectsJobSeekerProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    project_name = serializers.CharField()
    project_organization_name = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)

    class Meta:
        model = Projects
        fields = JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_3


class SkillSetJobSeekerProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    skill_name = serializers.CharField()
    proficiency_level = serializers.CharField()

    class Meta:
        model = SkillSet
        fields = JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_2


class JobSeekerGeneralProfileSerializer(serializers.ModelSerializer):
    aq_id = serializers.IntegerField(source="id", required=False)
    current_salary = serializers.DecimalField(
        source="user.sy_fk_user.current_salary",
        max_digits=10,
        decimal_places=2,
        default=None,
    )
    expected_salary = serializers.DecimalField(
        source="user.sy_fk_user.expected_salary",
        max_digits=10,
        decimal_places=2,
        default=None,
    )
    job_search_status = serializers.IntegerField(
        source="user.sy_fk_user.job_search_status",
        default=None,
    )
    notice_period = serializers.IntegerField(
        source="user.sy_fk_user.notice_period", default=None
    )
    sy_id = serializers.IntegerField(source="user.sy_fk_user.id", required=False)
    skill_sets = SkillSetJobSeekerProfileSerializer(
        required=True, many=True, source="user.ss_fk_user"
    )
    files = serializers.SerializerMethodField(read_only=True, default=[])

    def get_files(self, obj):
        try:
            return get_job_seeker_documents(
                user=obj.user,
                response_key_list=JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_4,
            )
        except Exception as e:
            return []

    def validate(self, data):
        if len(data["user"]["ss_fk_user"]) == 0:
            raise serializers.ValidationError(ATLEAST_ONE_SKILL_REQUIRED)
        return data

    def create(self, validated_data):
        user = self.context["request"].user

        # AQ Info
        aq_info_data = {"user": user}
        for key in JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_1:
            if validated_data[key] is not None:
                aq_info_data[key] = validated_data[key]
        aq_lookup = {
            "user": user.id,
        }
        if "id" in validated_data and validated_data["id"] is not None:
            aq_lookup["id"] = validated_data["id"]

        # Create, Update, Delete Skill Sets
        validated_ss_data = validated_data["user"]["ss_fk_user"]
        ss_operations = process_items(
            input_list=validated_ss_data,
            queryset=user.ss_fk_user.all(),
            extra_data={"user": user},
        )

        # SY Info
        sy_info_data = {
            "user": user,
        }
        validated_sy_data = validated_data["user"]["sy_fk_user"]
        for key in JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_3:
            if validated_sy_data[key] is not None:
                sy_info_data[key] = validated_sy_data[key]
        sy_lookup = {
            "user": user.id,
        }
        if "id" in validated_sy_data and validated_sy_data["id"] is not None:
            sy_lookup["id"] = validated_sy_data["id"]

        with transaction.atomic():
            # Create / Update Academic Qualification Info
            AcademicQualification.objects.update_or_create(
                **aq_lookup,
                defaults=aq_info_data,
            )

            # Skill Set Operation

            # Bulk delete: Delete items in the database that are not in payload
            if ss_operations["ids_to_delete"]:
                user.ss_fk_user.filter(id__in=ss_operations["ids_to_delete"]).delete()

            # Bulk create: Create items in the payload that are not in the database
            if ss_operations["items_to_create"]:
                user.ss_fk_user.bulk_create(ss_operations["items_to_create"])

            # Bulk update: Update items in the database that are in payload
            if ss_operations["items_to_update"]:
                user.ss_fk_user.bulk_update(
                    ss_operations["items_to_update"],
                    [
                        JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_2[1],
                        JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_2[2],
                    ],
                )

            # Create / Update Salary Info
            Salary.objects.update_or_create(
                **sy_lookup,
                defaults=sy_info_data,
            )

        return validated_data

    class Meta:
        model = AcademicQualification
        fields = JOB_SEEKER_PROFILE_GENERAL_INFO


class JobSeekerAdditionalProfileSerializer(serializers.ModelSerializer):
    work_experiences = WorkExperienceJobSeekerProfileSerializer(
        many=True, source="we_fk_user", default=[]
    )
    certifications = CertificationsJobSeekerProfileSerializer(
        many=True, source="ces_fk_user", default=[]
    )
    projects = ProjectsJobSeekerProfileSerializer(
        many=True, source="ps_fk_user", default=[]
    )

    def create(self, validated_data):
        user = self.context["request"].user

        # Create, Update, Delete Work Experiences
        validated_we_data = validated_data["we_fk_user"]
        we_operations = process_items(
            input_list=validated_we_data,
            queryset=user.we_fk_user.all(),
            extra_data={"user": user},
        )

        # Create, Update, Delete Certifications
        validated_ces_data = validated_data["ces_fk_user"]
        ces_operations = process_items(
            input_list=validated_ces_data,
            queryset=user.ces_fk_user.all(),
            extra_data={"user": user},
        )

        # Create, Update, Delete Projects
        validated_ps_data = validated_data["ps_fk_user"]
        ps_operations = process_items(
            input_list=validated_ps_data,
            queryset=user.ps_fk_user.all(),
            extra_data={"user": user},
        )

        with transaction.atomic():
            # Work Experiences Operation

            # Bulk delete: Delete items in the database that are not in payload
            if we_operations["ids_to_delete"]:
                user.we_fk_user.filter(id__in=we_operations["ids_to_delete"]).delete()

            # Bulk create: Create items in the payload that are not in the database
            if we_operations["items_to_create"]:
                user.we_fk_user.bulk_create(we_operations["items_to_create"])

            # Bulk update: Update items in the database that are in payload
            if we_operations["items_to_update"]:
                user.we_fk_user.bulk_update(
                    we_operations["items_to_update"],
                    [
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1[0],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1[1],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1[2],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1[3],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1[4],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1[5],
                    ],
                )

            # Certification Operation

            # Bulk delete: Delete items in the database that are not in payload
            if ces_operations["ids_to_delete"]:
                user.ces_fk_user.filter(id__in=ces_operations["ids_to_delete"]).delete()

            # Bulk create: Create items in the payload that are not in the database
            if ces_operations["items_to_create"]:
                user.ces_fk_user.bulk_create(ces_operations["items_to_create"])

            # Bulk update: Update items in the database that are in payload
            if ces_operations["items_to_update"]:
                user.ces_fk_user.bulk_update(
                    ces_operations["items_to_update"],
                    [
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_2[0],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_2[1],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_2[2],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_2[3],
                    ],
                )

            # Projects Operation

            # Bulk delete: Delete items in the database that are not in payload
            if ps_operations["ids_to_delete"]:
                user.ps_fk_user.filter(id__in=ps_operations["ids_to_delete"]).delete()

            # Bulk create: Create items in the payload that are not in the database
            if ps_operations["items_to_create"]:
                user.ps_fk_user.bulk_create(ps_operations["items_to_create"])

            # Bulk update: Update items in the database that are in payload
            if ps_operations["items_to_update"]:
                user.ps_fk_user.bulk_update(
                    ps_operations["items_to_update"],
                    [
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_3[0],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_3[1],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_3[2],
                        JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_3[3],
                    ],
                )

        return validated_data

    class Meta:
        model = WorkExperience
        fields = JOB_SEEKER_PROFILE_ADDITIONAL_INFO
