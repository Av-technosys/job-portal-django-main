from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from accounts.models import User
from accounts.serializers import UserMetaSerializer
from functions.common import create_new_handler, list_all_items_handler, delete_item_by_id_handler, get_item_by_id_handler, update_item_by_id_handler,get_question_by_subject_id_handler, get_test_question_handler, create_question_handler, create_payment_handler, get_payment_by_userid_handler, get_payment_by_id_handler, update_payment_by_id_handler, get_user_assesment_session_handler, get_all_assesment_attempts_handler, get_results_handler, submit_test_handler, get_free_test_question_handler, upload_question_image_handler, ResponseHandler
from handlers.permissions import IsRecruiter
from user_profiles.models import StudentProfile

# Create your views here.

# Subjects
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_Subject(request):
    return create_new_handler(SubjectSerializer, request)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_all_subjects(request):
    return list_all_items_handler(Subject ,SubjectSerializer, request)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_subject_by_id(request, item_id):
    return get_item_by_id_handler(Subject, item_id, SubjectSerializer, request)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_subject(request):
    return delete_item_by_id_handler(Subject , request)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_subject(request):
    return update_item_by_id_handler(Subject, SubjectSerializer, request)



# Questions
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_question(request):
    return create_question_handler(QuestionsSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_all_questions(request):
    return list_all_items_handler(Question ,QuestionsSerializer, request)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_question_by_subject_id(request, subject_id):
    return get_question_by_subject_id_handler(Question ,QuestionsSerializer,subject_id, request)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_test_question(request): 
    return get_test_question_handler(Question, Subject, AssessmentSession, Attempt, AttemptSerializerSave,TestQuestionSerializer, request)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_free_test_question(request): 
    return get_free_test_question_handler(Question, Subject, AttemptSerializerSave,TestQuestionSerializer, request)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_question_by_id(request, item_id):
    return get_item_by_id_handler(Question, item_id, QuestionsSerializer, request)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_question(request):
    return delete_item_by_id_handler(Question , request)


@api_view(["DELETE", "POST", "PATCH"])
@permission_classes([IsAuthenticated])
def upload_question_image(request):
    return upload_question_image_handler(Question, QuestionsSerializer , request)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_question(request):
    return update_item_by_id_handler(Question, QuestionsSerializer, request)




# Payment
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment(request):
    return create_payment_handler(PaymentSerializer, AssessmentSessionSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_payment_by_userid(request, user_id):
    return get_payment_by_userid_handler(Payment ,PaymentSerializer, user_id, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_payment_by_id(request, item_id):
    return get_payment_by_id_handler(Payment ,PaymentSerializer, item_id, request)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_payment_by_id(request): 
    return update_payment_by_id_handler(Payment, PaymentSerializer, AssessmentSessionSerializer, request)




# Assesment
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_assesment_by_id(request, item_id): 
    return get_item_by_id_handler(AssessmentSession ,item_id ,AssessmentSessionSerializer, request)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_assesment_by_id(request): 
    return update_item_by_id_handler(AssessmentSession ,AssessmentSessionSerializer, request)

# Assesment
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_assesment_session(request): 
    return get_user_assesment_session_handler(User ,AssessmentSession ,AssessmentSessionSerializer, { "email": request.user}, request)

# Assesment
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_assesment_attempts(request, session_id): 
    return get_all_assesment_attempts_handler(User , Attempt ,AttemptSerializer, { "email": request.user}, session_id, request)

# Assesment
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsRecruiter])
def get_applicant_assesment_attempts(request, applicant_id):
    applicant_user_ids = {applicant_id}

    student_profile = StudentProfile.objects.filter(id=applicant_id).first()
    if student_profile:
        applicant_user_ids.add(student_profile.user_id)

    user_student_profile = StudentProfile.objects.filter(user_id=applicant_id).first()
    if user_student_profile:
        applicant_user_ids.add(user_student_profile.user_id)

    attempts = Attempt.objects.filter(
        user_id__in=applicant_user_ids,
    ).select_related("subject", "assessment_session").order_by("-updated_at", "-id")
    response_data = []

    for attempt in attempts:
        assessment_total = attempt.maximum_possible_score
        total_marks_scored = attempt.score

        if total_marks_scored is None or assessment_total is None:
            total_answers = attempt.answers.count()
            total_questions = (
                attempt.subject.easy_question_count
                + attempt.subject.medium_question_count
                + attempt.subject.difficult_question_count
            )
            not_answered_calc = (
                total_questions - total_answers
            ) * attempt.subject.marks_unattempted
            assessment_total = total_questions * attempt.subject.marks_correct
            total_marks_scored = not_answered_calc + (
                total_answers * attempt.subject.marks_correct
            )

            attempt.score = total_marks_scored
            attempt.maximum_possible_score = assessment_total
            attempt.save(update_fields=["score", "maximum_possible_score", "updated_at"])

        response_data.append(
            {
                "id": attempt.id,
                "attempt_id": attempt.id,
                "subject_id": attempt.subject_id,
                "subject_name": attempt.subject.exam_name,
                "section_name": attempt.subject.section_name,
                "score": total_marks_scored,
                "total_marks_scored": total_marks_scored,
                "assessment_total": assessment_total,
                "assesment_total": assessment_total,
                "maximum_possible_score": assessment_total,
                "assessment_session_id": getattr(attempt.assessment_session, "id", 0),
                "assesment_session_id": getattr(attempt.assessment_session, "id", 0),
                "submit_time": attempt.submit_time,
                "created_at": attempt.created_at,
                "updated_at": attempt.updated_at,
                "status": attempt.status,
            }
        )

    return ResponseHandler.success(response_data, status_code=200)

# Assesment
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_results(request, attempt_id): 
    return get_results_handler(Attempt, AttemptAnswer, attempt_id, request)

# Assesment
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_test(request, attempt_id): 
    return submit_test_handler(Attempt, AttemptAnswer, Question, attempt_id, request)
