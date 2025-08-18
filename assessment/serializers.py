from rest_framework import serializers
from .models import Subject, Question

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class QuestionsSerializer(serializers.ModelSerializer):
    Subject = SubjectSerializer(read_only=True)
    class Meta:
        model = Question
        fields = "__all__"