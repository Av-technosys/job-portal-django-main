from rest_framework import serializers
from .models import JobInfo, JobContactInfo, JobDescription
from constants.jobs import (
    JOB_INFO_META_FIELD,
    JOB_CONTACT_INFO_META_FIELD,
    JOB_DESCRIPTION_META_FIELD,
)


# Serializer for JobDetails model (Section 1)
class JobInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInfo
        fields = JOB_INFO_META_FIELD


# Serializer for JobContactInfo model (Section 2)
class JobContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobContactInfo
        fields = JOB_CONTACT_INFO_META_FIELD


# Serializer for JobDescription model (Section 3)
class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = JOB_DESCRIPTION_META_FIELD
