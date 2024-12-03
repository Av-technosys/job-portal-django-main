from rest_framework import serializers
from user_profiles.models import FCMToken
from functions.fcm import (
    save_notification,
    send_notification_to_topic,
    subscribe_to_topic,
)
from constants.user_profiles import (
    NOTIFICATION_TYPE_CHOICES_ID,
    NOTIFICATION_TYPE_CHOICES_TITLE,
)
from .models import *
from constants.errors import ALREADY_APPLIED, INVALID_JOB_STATUS
from constants.jobs import JOB_DETAILS_FIELDS, VALID_STATUS_TRANSITIONS
from rest_framework.authtoken.models import Token


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
        self.send_notification()
        return job

    def send_notification(self):
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

            # TBD Email to the student about application submitted
            recruiter_token_details = Token.objects.get(user=recruiter_id)

            # Send Notification only if logged in
            if recruiter_token_details:

                try:
                    # Send Firebase notification
                    recruiter_fcm_token = FCMToken.objects.get(
                        user=recruiter_id
                    ).fcm_token
                    topic_name = f"bell_{recruiter_id}"
                    subscribe_to_topic(recruiter_fcm_token, topic_name)

                    send_notification_to_topic(
                        topic_name,
                        NOTIFICATION_TYPE_CHOICES_TITLE[0]["notification_title"],
                        NOTIFICATION_TYPE_CHOICES_TITLE[0]["notification_body"],
                    )

                except FCMToken.DoesNotExist:
                    print(
                        "Recruiter doesn't have any active fcm session Skipping Sending Notification"
                    )

                except Exception as e:
                    print(e, "err")

        except Token.DoesNotExist:
            print(
                "Recruiter doesn't have any active session Skipping Sending Notification"
            )

        except Exception as e:
            print("Error while sending notification", e)
