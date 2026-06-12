from rest_framework import serializers
from .models import Subject, Question, Payment, AssessmentSession ,Attempt, AttemptAnswer

class SubjectSerializer(serializers.ModelSerializer):
    available_easy_questions = serializers.SerializerMethodField()
    available_medium_questions = serializers.SerializerMethodField()
    available_difficult_questions = serializers.SerializerMethodField()
    is_ready = serializers.SerializerMethodField()
    readiness_details = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = "__all__"

    def _question_count(self, obj, difficulty_level):
        return obj.questions.filter(difficulty_level=difficulty_level).count()

    def _readiness_details(self, obj):
        difficulty_config = [
            ("easy", obj.easy_question_count, self._question_count(obj, 1)),
            ("medium", obj.medium_question_count, self._question_count(obj, 2)),
            ("difficult", obj.difficult_question_count, self._question_count(obj, 3)),
        ]
        return [
            {
                "difficulty": label,
                "required": required,
                "available": available,
                "missing": max(required - available, 0),
            }
            for label, required, available in difficulty_config
        ]

    def get_available_easy_questions(self, obj):
        return self._question_count(obj, 1)

    def get_available_medium_questions(self, obj):
        return self._question_count(obj, 2)

    def get_available_difficult_questions(self, obj):
        return self._question_count(obj, 3)

    def get_is_ready(self, obj):
        return all(item["missing"] == 0 for item in self._readiness_details(obj))

    def get_readiness_details(self, obj):
        return self._readiness_details(obj)

    def validate(self, attrs):
        is_live = attrs.get("is_live", self.instance.is_live if self.instance else False)

        if not is_live:
            return attrs

        if not self.instance:
            raise serializers.ValidationError({
                "is_live": "Add the subject first, then publish it after enough questions are added."
            })

        easy_required = attrs.get("easy_question_count", self.instance.easy_question_count)
        medium_required = attrs.get("medium_question_count", self.instance.medium_question_count)
        difficult_required = attrs.get("difficult_question_count", self.instance.difficult_question_count)
        missing_questions = []

        difficulty_config = [
            ("easy", easy_required, self.instance.questions.filter(difficulty_level=1).count()),
            ("medium", medium_required, self.instance.questions.filter(difficulty_level=2).count()),
            ("difficult", difficult_required, self.instance.questions.filter(difficulty_level=3).count()),
        ]

        for label, required, available in difficulty_config:
            if available < required:
                missing_questions.append(
                    f"{label}: required {required}, available {available}"
                )

        if missing_questions:
            raise serializers.ValidationError({
                "is_live": "Subject cannot be published yet. " + "; ".join(missing_questions)
            })

        return attrs


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
    order = serializers.PrimaryKeyRelatedField(read_only=True)

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
