from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from functions.common import create_new_handler, list_all_items_handler, delete_item_by_id_handler, get_item_by_id_handler, update_item_by_id_handler,get_question_by_subject_id_handler, get_test_by_subject_id_handler, create_question_handler, create_payment_handler, get_payment_by_userid_handler, get_payment_by_id_handler, update_payment_by_id_handler

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
def get_test_by_subject_id(request, subject_id): 
    return get_test_by_subject_id_handler(Question, Subject, TestQuestionSerializer, subject_id, request)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_question_by_id(request, item_id):
    return get_item_by_id_handler(Question, item_id, QuestionsSerializer, request)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_question(request):
    return delete_item_by_id_handler(Question , request)

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