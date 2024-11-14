from rest_framework import serializers
from .models import *
from constants.jobs import JOB_DETAILS_FIELDS


# Serializer for JobDetails model (Section 1)
class JobInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobInfo
        fields = "__all__"


# Serializer for JobContactInfo model (Section 2)
class JobContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobContactInfo
        fields = "__all__"


# Serializer for JobDescription model (Section 3)
class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = "__all__"


class CombinedJobDetailsSerializer(serializers.ModelSerializer):
    contact_info = JobContactInfoSerializer(read_only=True)
    description = JobDescriptionSerializer(read_only=True)

    class Meta:
        model = JobInfo
        fields = JOB_DETAILS_FIELDS
        
class JobApplySerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    class Meta:
        model = JobApply
        fields = "__all__"