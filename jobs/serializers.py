from rest_framework import serializers
from .models import Jobs
from constants.jobs import *


# Section 1 Serializer
class Section1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = SECTION_1_META_FIELD


# Section 2 Serializer
class Section2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = SECTION_2_META_FIELD


# Section 3 Serializer
class Section3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = SECTION_3_META_FIELD
