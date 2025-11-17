from rest_framework import serializers
from .models import Subject, Question, Payment, AssessmentSession ,Attempt, AttemptAnswer

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class QuestionsSerializer(serializers.ModelSerializer):
    Subject = SubjectSerializer(read_only=True)
    class Meta:
        model = Question
        fields = "__all__"


class TestQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "option_1",
            "option_2",
            "option_3",
            "option_4",
            "question_image",
        ]




class PaymentSerializer(serializers.ModelSerializer):
    Subject = SubjectSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = "__all__"



class AssessmentSessionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True) 
    order = serializers.CharField(read_only=True)

    class Meta:
        model = AssessmentSession
        fields = [
            "id",
            "order",
            "user",
            "overall_score",
            "complete_percentage",
            "is_test_end",
            "status",
            "created_at",
            "updated_at",
        ]

class AttemptSerializer(serializers.ModelSerializer): 
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    subject = serializers.StringRelatedField() 
    subject_id = serializers.PrimaryKeyRelatedField(read_only=True)
    assessment_session = serializers.PrimaryKeyRelatedField(read_only=True)
     
    status = serializers.ChoiceField(choices=Attempt.STATUS_CHOICES)

    class Meta:
        model = Attempt
        fields = "__all__"


class AttemptSerializerSave(serializers.ModelSerializer): 
    class Meta:
        model = Attempt
        fields = "__all__"


class AttemptAnswerSerializer(serializers.ModelSerializer): 
    # user = serializers.PrimaryKeyRelatedField(read_only=True)
    # subject = serializers.StringRelatedField() 
    # assessment_session = serializers.PrimaryKeyRelatedField(read_only=True)
     
    # status = serializers.ChoiceField(choices=Attempt.STATUS_CHOICES)

    class Meta:
        model = AttemptAnswer
        fields = "__all__"