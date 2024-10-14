from rest_framework import serializers
from .models import JobInfo, JobContactInfo, JobDescription


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
