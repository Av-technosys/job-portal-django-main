from rest_framework import serializers
from functions.fcm import save_notification, send_notification
from constants.user_profiles import (
    NOTIFICATION_TYPE_CHOICES_ID,
    NOTIFICATION_TYPE_CHOICES_TITLE,
)
from functions.common import logger
from functions.send_email import (
    send_application_confirmation_to_job_seeker,
    send_application_received_to_recruiter,
)
from user_profiles.models import CompanyProfile
from .models import *
from constants.errors import ALREADY_APPLIED, INVALID_JOB_STATUS, ALREADY_SAVED
from constants.jobs import (
    JOB_DETAILS_FIELDS,
    VALID_STATUS_TRANSITIONS,
    JOB_LIST_SEEKER_VIEW_FEILDS,
    JOB_APPLIED_VIEW_FEILDS,
    JOB_POSTED_VIEW_FEILDS
)

from functions.common import get_user_photo
from user_profiles.models import UploadedFile


# Serializer for JobDetails model (Section 1)
# Serializer for JobDetails model (Section 1)
class JobDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInfo
        fields = "__all__"


# Serializer for JobDescription model (Section 2)
class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = "__all__"


# Serializer for ContactAndSkills model (Section 2)
class ContactAndSkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactAndSkills
        fields = "__all__"


# Serializer for JobOverviewAndQualifications model (Section 3)
class JobOverviewAndQualificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOverviewAndQualifications
        fields = "__all__"


# Serializer for SkillsCertificationsResponsibilities model (Section 3)
class SkillsCertificationsResponsibilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsCertificationsResponsibilities
        fields = "__all__"


# Combined Serializer for JobDetails (Nested)
class CombinedJobDetailsSerializer(serializers.ModelSerializer):
    # Nested serializers for related models
    job_description = JobDescriptionSerializer(many=True, read_only=True)
    contact_and_skills = ContactAndSkillsSerializer(many=True, read_only=True)
    job_overview_and_qualifications = JobOverviewAndQualificationsSerializer(
        many=True, read_only=True
    )
    skills_certifications_responsibilities = (
        SkillsCertificationsResponsibilitiesSerializer(many=True, read_only=True)
    )

    class Meta:
        model = JobInfo
        fields = JOB_DETAILS_FIELDS


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
            recruiter_details = CompanyProfile.objects.filter(user=recruiter_id).first()
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


class JobListingSeekerViewSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    salary_range = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    company_profile_image = serializers.SerializerMethodField()

    class Meta:
        model = JobInfo
        fields = JOB_LIST_SEEKER_VIEW_FEILDS

    def get_company_name(self, obj):
        job_description = obj.job_description.first()
        return job_description.company_name if job_description else None

    def get_salary_range(self, obj):
        job_overview = obj.job_overview_and_qualifications.first()
        return job_overview.salary_range if job_overview else None

    def get_is_applied(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return JobApply.objects.filter(job=obj, student_id=request.user.id).exists()
        return False

    def get_company_profile_image(self, obj):
        return get_user_photo(obj.user, UploadedFile)


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

class AppliedJobListViewSerializer(serializers.ModelSerializer):
    designation = serializers.CharField(source="job.designation")
    location = serializers.CharField(source="job.location")
    job_type = serializers.CharField(source="job.job_type")
    salary_range = serializers.SerializerMethodField()
    applied_date = serializers.DateTimeField(source="created_date")
    job_id = serializers.IntegerField(source="job.id")
    application_id = serializers.IntegerField(source="id")

    class Meta:
        model = JobApply
        fields = JOB_APPLIED_VIEW_FEILDS

    def get_salary_range(self, obj):
        job_overview = obj.job.job_overview_and_qualifications.first()
        return job_overview.salary_range if job_overview else None

class JobPostedListSerializer(serializers.ModelSerializer):
    salary_range = serializers.SerializerMethodField()
    applicants_count = serializers.SerializerMethodField()

    class Meta:
        model = JobInfo
        fields = JOB_POSTED_VIEW_FEILDS

    def get_salary_range(self, obj):
        overview = obj.job_overview_and_qualifications.first()
        return overview.salary_range if overview else 0

    def get_applicants_count(self, obj):
        return obj.applications.count()