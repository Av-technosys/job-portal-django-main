from rest_framework import serializers
from functions.fcm import save_notification, send_notification
from constants.user_profiles import (
    NOTIFICATION_TYPE_CHOICES_ID,
    NOTIFICATION_TYPE_CHOICES_TITLE,
)
from functions.common import (
    get_location_formatted,
    get_recruiter_profile_image,
    get_salary_formatted,
    is_job_seeker,
    logger,
)
from functions.send_email import (
    send_application_confirmation_to_job_seeker,
    send_application_received_to_recruiter,
)
from .models import *
from constants.errors import ALREADY_APPLIED, INVALID_JOB_STATUS, ALREADY_SAVED
from constants.jobs import (
    VALID_STATUS_TRANSITIONS,
    JOB_SEEKER_LIST_VIEW_FIELDS,
    JOB_APPLIED_VIEW_FIELDS,
    JOB_POSTED_VIEW_FEILDS,
    JOB_INFO_SERIALIZER_FEILDS,
    JOB_DESCRIPTION_SERIALIZER_FEILDS,
)

from functions.common import get_user_photo
from user_profiles.models import OrganizationInfo, RecruiterUploadedFile


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
    skills = serializers.CharField()
    description = serializers.CharField()

    def create(self, validated_data):
        user = self.context["request"].user
        job_info_data = {
            field: validated_data[field] for field in JOB_INFO_SERIALIZER_FEILDS
        }
        job_info_data["user"] = user
        job_info = JobInfo.objects.create(**job_info_data)
        job_description_data = {
            field: validated_data[field] for field in JOB_DESCRIPTION_SERIALIZER_FEILDS
        }
        job_description_data["job"] = job_info  # Link to JobInfo instance
        job_description_data["user"] = user  # Link the user
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
            recruiter_details = OrganizationInfo.objects.filter(
                user=recruiter_id
            ).first()
            job_details = JobInfo.objects.filter(pk=job_id).first()

            send_application_confirmation_to_job_seeker(
                student_details, recruiter_details, job_details
            )

            send_application_received_to_recruiter(
                student_details, recruiter_details, job_details
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
    is_applied = serializers.SerializerMethodField()
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

    def get_is_applied(self, obj):
        if self.check_for_meta_data():
            job_seeker_id = self.get_logged_in_job_seeker_id()
            return obj.job_id_applied.filter(student=job_seeker_id).exists()
        return False

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
    job_type = serializers.CharField(source="job.job_type")
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


class JobPostedListSerializer(serializers.ModelSerializer):
    company_profile_image = serializers.SerializerMethodField()
    title = serializers.CharField()
    salary = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    application_count = serializers.IntegerField(source="applications.count")
    job_id = serializers.IntegerField(source="id")

    class Meta:
        model = JobInfo
        fields = JOB_POSTED_VIEW_FEILDS

    def get_company_profile_image(self, obj):
        return get_user_photo(obj.user, RecruiterUploadedFile)

    def get_salary(self, obj):
        return get_salary_formatted(obj)

    def get_location(self, obj):
        return get_location_formatted(obj)
