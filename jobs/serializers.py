from rest_framework import serializers
from .models import *
from constants.errors import ALREADY_APPLIED, INVALID_JOB_STATUS
from constants.jobs import JOB_DETAILS_FIELDS, VALID_STATUS_TRANSITIONS


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
    job_description = JobDescriptionSerializer(
        many=True, read_only=True
    )
    contact_and_skills = ContactAndSkillsSerializer(
        many=True, read_only=True
    )
    job_overview_and_qualifications = JobOverviewAndQualificationsSerializer(
        many=True, read_only=True
    )
    skills_certifications_responsibilities = (
        SkillsCertificationsResponsibilitiesSerializer(
            many=True, read_only=True
        )
    )

    class Meta:
        model = JobInfo
        fields = JOB_DETAILS_FIELDS


class JobApplySerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source="user", read_only=True)

    class Meta:
        model = JobApply
        fields = "__all__"

    def validate(self, data):
        job_apply_instance = self.instance
        new_status = data.get("status")

        if job_apply_instance and new_status is not None:
            current_status = job_apply_instance.status 
            if new_status not in VALID_STATUS_TRANSITIONS.get(current_status, []):
                raise serializers.ValidationError(
                     {"message": INVALID_JOB_STATUS}
                )
        student = data.get("student")
        job = data.get("job")
        if JobApply.objects.filter(student=student, job=job).exists():
            raise serializers.ValidationError({"message": ALREADY_APPLIED})

        return data
