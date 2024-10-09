from rest_framework import serializers
from .models import Jobs

# Section 1 Serializer
class Section1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = ['designation', 'department', 'location', 'job_type', 'status']

# Section 2 Serializer
class Section2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = ['job_description', 'contact_name', 'phone_number', 'email', 'skills_required']

# Section 3 Serializer
class Section3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = ['job_overview', 'qualifications_and_skills', 'roles_and_responsibilities']
