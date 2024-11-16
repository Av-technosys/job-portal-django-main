from rest_framework import serializers
from .models import *
from constants.errors import ALREADY_APPLIED
from constants.jobs import JOB_DETAILS_FIELDS


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
        many=True, read_only=True, source="job_description"
    )
    contact_and_skills = ContactAndSkillsSerializer(
        many=True, read_only=True, source="contact_and_skills"
    )
    job_overview_and_qualifications = JobOverviewAndQualificationsSerializer(
        many=True, read_only=True, source="job_overview_and_qualifications"
    )
    skills_certifications_responsibilities = (
        SkillsCertificationsResponsibilitiesSerializer(
            many=True, read_only=True, source="skills_certifications_responsibilities"
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
        # Check if a JobApply entry already exists for the given student and job
        student = data.get("student")
        job = data.get("job")

        if JobApply.objects.filter(student=student, job=job).exists():
            raise serializers.ValidationError({"message": ALREADY_APPLIED})

        return data
