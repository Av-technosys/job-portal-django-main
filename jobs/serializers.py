from rest_framework import serializers
from functions.fcm import save_notification, send_notification
from constants.user_profiles import (
    NOTIFICATION_TYPE_CHOICES_ID,
    NOTIFICATION_TYPE_CHOICES_TITLE,
)
from functions.common import (
    get_days_remaining_for_job,
    get_job_post_status,
    get_location_formatted,
    get_recruiter_profile_image,
    get_salary_formatted,
    is_job_seeker,
    logger,
    get_expired_date,
    get_organization_type_from_models,
)
from functions.send_email import (
    send_application_confirmation_to_job_seeker,
    send_application_received_to_recruiter,
)
from user_profiles.serializers import SocialLinkItemSerializer
from .models import *
from constants.errors import ALREADY_APPLIED, INVALID_JOB_STATUS, ALREADY_SAVED
from constants.jobs import (
    JOB_APPLIED_VIEW_FIELDS,
    JOB_DESCRIPTION_SERIALIZER_FEILDS,
    JOB_DETAILS_COMBINED_FIELDS,
    JOB_INFO_SERIALIZER_FEILDS,
    JOB_POSTED_VIEW_FEILDS,
    JOB_SEEKER_LIST_VIEW_FIELDS,
    SAVED_JOBS_JOB_SEEKER_LIST_VIEW_FIELDS,
    VALID_STATUS_TRANSITIONS,
)

from user_profiles.models import FoundingInfo
from django.db import transaction


class JobInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInfo
        fields = "__all__"


class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = "__all__"


class JobCombinedSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    role = serializers.CharField(max_length=100)
    max_salary = serializers.IntegerField()
    min_salary = serializers.IntegerField()
    job_type = serializers.CharField(max_length=50)
    job_level = serializers.CharField(max_length=100)
    vacancies = serializers.IntegerField()
    education = serializers.CharField(max_length=100)
    experience = serializers.IntegerField()
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    skills = serializers.ListField(
        child=serializers.CharField(max_length=50), allow_empty=True
    )
    description = serializers.CharField()
    expiration_days = serializers.IntegerField(required=True)
    date_of_birth = serializers.DateField(format="%Y-%m-%d")

    def create(self, validated_data):
        user = self.context["request"].user
        expiration_days = validated_data["expiration_days"]
        expired_at = get_expired_date(expiration_days)
        job_info_data = {
            field: validated_data[field] for field in JOB_INFO_SERIALIZER_FEILDS
        }
        job_info_data["user"] = user
        job_info_data["expired_at"] = expired_at
        job_description_data = {
            field: validated_data[field] for field in JOB_DESCRIPTION_SERIALIZER_FEILDS
        }
        job_description_data["user"] = user
        with transaction.atomic():
            job_info = JobInfo.objects.create(**job_info_data)
            job_description_data["job"] = job_info
            JobDescription.objects.create(**job_description_data)

        return validated_data


class JobApplySerializer(serializers.ModelSerializer):

    class Meta:
        model = JobApply
        fields = "__all__"

    def validate(self, data):
        job_apply_instance = self.instance
        new_status = data.get("status")

        if job_apply_instance and new_status is not None:
            current_status = job_apply_instance.status
            if new_status not in VALID_STATUS_TRANSITIONS.get(current_status, []):
                raise serializers.ValidationError({"message": INVALID_JOB_STATUS})
        student = data.get("student")
        job = data.get("job")
        if JobApply.objects.filter(student=student, job=job).exists():
            raise serializers.ValidationError({"message": ALREADY_APPLIED})

        return data

    def save(self):
        job = super().save()
        self.send_apply_notification()
        self.send_email_confirmation_for_the_application()
        return job

    def send_email_confirmation_for_the_application(self):
        try:
            job_id = self.data.get("job")
            recruiter_id = self.data.get("owner")
            student_id = self.data.get("student")

            student_details = User.objects.filter(pk=student_id).first()
            recruiter_personal_details = User.objects.filter(pk=recruiter_id).first()
            recruiter_details = FoundingInfo.objects.filter(user=recruiter_id).first()
            job_details = JobInfo.objects.filter(pk=job_id).first()

            send_application_confirmation_to_job_seeker(
                student_details,
                recruiter_details,
                job_details,
                recruiter_personal_details,
            )

            send_application_received_to_recruiter(
                student_details,
                recruiter_details,
                job_details,
                recruiter_personal_details,
            )

        except Exception as e:
            logger.error(f"Error in send_email_confirmation_for_the_application: {e}")

    def send_apply_notification(self):
        try:
            job_id = self.data.get("job")
            recruiter_id = self.data.get("owner")
            student_id = self.data.get("student")

            # Save notification to the database
            save_notification(
                {
                    "type": NOTIFICATION_TYPE_CHOICES_ID[0],
                    "body": NOTIFICATION_TYPE_CHOICES_TITLE[0]["notification_title"],
                    "metadata": {"job_id": job_id},
                },
                recruiter_id,
                student_id,
            )

            send_notification(
                recruiter_id, f"bell_{recruiter_id}", NOTIFICATION_TYPE_CHOICES_ID[0]
            )

        except Exception as e:
            print("Error while sending send_apply_notification", e)


class CommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Communication
        fields = "__all__"

    def save(self):
        message = super().save()
        self.send_message_notification()
        return message

    def send_message_notification(self):
        application_id = self.data.get("application")
        received_by = self.data.get("received_by")

        send_notification(
            received_by,
            f"message_{application_id}_{received_by}",
            NOTIFICATION_TYPE_CHOICES_ID[1],
        )


class JobSeekerListingViewSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    company_profile_image = serializers.SerializerMethodField()

    class Meta:
        model = JobInfo
        fields = JOB_SEEKER_LIST_VIEW_FIELDS

    def check_for_meta_data(self):
        request = self.context.get("request")
        return is_job_seeker(request)

    def get_logged_in_job_seeker_id(self):
        return self.context.get("request").user.id

    def get_company_name(self, obj):
        return obj.user.first_name

    def get_salary(self, obj):
        return get_salary_formatted(obj)

    def get_location(self, obj):
        return get_location_formatted(obj)

    def get_is_saved(self, obj):
        if self.check_for_meta_data():
            job_seeker_id = self.get_logged_in_job_seeker_id()
            return obj.saved_job.filter(user=job_seeker_id).exists()
        return False

    def get_company_profile_image(self, obj):
        return get_recruiter_profile_image(obj.user)


class SavedJobsJobSeekerListingViewSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    company_profile_image = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = JobInfo
        fields = SAVED_JOBS_JOB_SEEKER_LIST_VIEW_FIELDS

    def check_for_meta_data(self):
        request = self.context.get("request")
        return is_job_seeker(request)

    def get_logged_in_job_seeker_id(self):
        return self.context.get("request").user.id

    def get_company_name(self, obj):
        return obj.user.first_name

    def get_salary(self, obj):
        return get_salary_formatted(obj)

    def get_location(self, obj):
        return get_location_formatted(obj)

    def get_is_applied(self, obj):
        if self.check_for_meta_data():
            job_seeker_id = self.get_logged_in_job_seeker_id()
            return obj.job_id_applied.filter(student=job_seeker_id).exists()
        return False

    def get_days_remaining(self, obj):
        return get_days_remaining_for_job(obj)

    def get_company_profile_image(self, obj):
        return get_recruiter_profile_image(obj.user)


class JobSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSaved
        fields = "__all__"

    def validate(self, data):
        user = data.get("user")
        job = data.get("job")

        if JobSaved.objects.filter(user=user, job=job).exists():
            raise serializers.ValidationError({"message": ALREADY_SAVED})

        return data


class CandidateSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSaved
        fields = "__all__"


class AppliedJobListViewSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="job.title")
    salary = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    company_profile_image = serializers.SerializerMethodField()
    job_type = serializers.CharField(source="job.job_type")
    role = serializers.CharField(source="job.role")
    applied_date = serializers.DateTimeField(source="created_date")
    job_id = serializers.IntegerField(source="job.id")
    application_id = serializers.IntegerField(source="id")

    class Meta:
        model = JobApply
        fields = JOB_APPLIED_VIEW_FIELDS

    def get_salary(self, obj):
        return get_salary_formatted(obj.job)

    def get_location(self, obj):
        return get_location_formatted(obj.job)

    def get_company_profile_image(self, obj):
        return get_recruiter_profile_image(obj.job.user)


class JobPostedListSerializer(serializers.ModelSerializer):
    company_profile_image = serializers.SerializerMethodField()
    role = serializers.CharField()
    title = serializers.CharField()
    salary = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    application_count = serializers.IntegerField(source="job_id_applied.count")
    job_id = serializers.IntegerField(source="id")
    job_status = serializers.SerializerMethodField()

    class Meta:
        model = JobInfo
        fields = JOB_POSTED_VIEW_FEILDS

    def get_company_profile_image(self, obj):
        return get_recruiter_profile_image(obj.user)

    def get_salary(self, obj):
        return get_salary_formatted(obj)

    def get_location(self, obj):
        return get_location_formatted(obj)

    def get_job_status(self, obj):
        return get_job_post_status(obj)


class JobDetailsCombinedSerializer(serializers.ModelSerializer):
    company_profile_image = serializers.SerializerMethodField()
    job_id = serializers.IntegerField(source="id")
    company_name = serializers.SerializerMethodField()
    organization_type = serializers.SerializerMethodField()
    job_status = serializers.SerializerMethodField()
    title = serializers.CharField()
    role = serializers.CharField()
    salary = serializers.SerializerMethodField()
    job_type = serializers.CharField()
    job_level = serializers.CharField()
    vacancies = serializers.IntegerField()
    education = serializers.CharField(source="jd_fk_ji.education", default="")
    experience = serializers.IntegerField(source="jd_fk_ji.experience", default=False)
    location = serializers.SerializerMethodField(source="jd_fk_ji.location", default="")
    skills = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        source="jd_fk_ji.skills",
        default=[],
    )
    description = serializers.CharField(source="jd_fk_ji.description", default="")
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = JobInfo
        fields = JOB_DETAILS_COMBINED_FIELDS

    def get_company_profile_image(self, obj):
        return get_recruiter_profile_image(obj.user)

    def get_company_name(self, obj):
        return obj.user.first_name

    def get_salary(self, obj):
        return get_salary_formatted(obj)

    def get_location(self, obj):
        return get_location_formatted(obj)

    def get_job_status(self, obj):
        return get_job_post_status(obj)

    def get_social_links(self, obj):
        sl = obj.user.sml_r_fk_user.all()
        if sl:
            sl_data = SocialLinkItemSerializer(sl, many=True).data
            if sl_data:
                return sl_data
        return []

    def get_organization_type(self, obj):
        # Use the renamed standalone function
        return get_organization_type_from_models(obj)


class JobStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInfo
        fields = ["status"]

    def validate_status(self, value):
        valid_statuses = [status[0] for status in JOB_POST_STATUS_FEILDS]
        if value not in valid_statuses:
            raise serializers.ValidationError(INVALID_JOB_STATUS)
        return value
