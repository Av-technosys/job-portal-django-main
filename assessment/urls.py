
from django.urls import path
from .views import *


urlpatterns = [
    
        # Subjects
        path("create_Subject/", create_Subject, name="create_Subject"),
        path("list_all_subjects/", list_all_subjects, name="list_all_subjects"),
        path("get_subject_by_id/<int:item_id>/",get_subject_by_id, name="get_subject_by_id"),
        path("update_subject/", update_subject, name="update_subject"),
        path("delete_subject/", delete_subject, name="delete_subject"),


        # Questions
        path("get_question_by_id/<int:item_id>/",get_question_by_id, name="get_question_by_id"),
        path("create_question/", create_question, name="create_question"),
        path("list_all_questions/", list_all_questions, name="list_all_questions"), 
        path("get_question_by_subject_id/<int:subject_id>/", get_question_by_subject_id, name="get_question_by_subject_id"), 
        path("update_question/", update_question, name="update_question"),
        path("delete_question/", delete_question, name="delete_question"),

        # Payments
        path("create_payment/", create_payment, name="create_payment"),
        path("get_payment_by_userid/<int:user_id>/", get_payment_by_userid, name="get_payment_by_userid"),
        path("get_payment_by_id/<int:item_id>/", get_payment_by_id, name="get_payment_by_userid"),
        path("update_payment_by_id/", update_payment_by_id, name="get_payment_by_userid"),


        # Assesment Section
        path("get_assesment_by_id/<int:item_id>/", get_assesment_by_id, name="get_assesment_by_id"),
        path("update_assesment_by_id/", update_assesment_by_id, name="update_assesment_by_id"),

        path("get_user_assesment_session/", get_user_assesment_session, name="get_user_assesment_session"),
        path("get_all_assesment_attempts/<int:session_id>/", get_all_assesment_attempts, name="get_all_assesment_attempts"),
        path("get_results/<int:attempt_id>/", get_results, name="get_results"),
        path("submit_test/<int:attempt_id>/", submit_test, name="submit_test"),
        # path("update_user_assesment_session/", update_user_assesment_session, name="update_user_assesment_session"),

        # Test
        # Assesment_session and subject_id 
        path("get_test_question/", get_test_question, name="get_test_question"),
        path("get_free_test_question/", get_free_test_question, name="get_free_test_question"),
        
]