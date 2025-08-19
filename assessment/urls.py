
from django.urls import path
from .views import *


urlpatterns = [
    
        # path related to subjects

        path("create_Subject/", create_Subject, name="create_Subject"),
        path("list_all_subjects/", list_all_subjects, name="list_all_subjects"),
        path("get_subject_by_id/<int:item_id>/",get_subject_by_id, name="get_subject_by_id"),
        path("update_subject/", update_subject, name="update_subject"),
        path("delete_subject/", delete_subject, name="delete_subject"),


        # path related to questions

        path("get_question_by_id/<int:item_id>/",get_question_by_id, name="get_question_by_id"),
        path("create_question/", create_question, name="create_question"),
        path("upload_question_image/", upload_question_image, name="upload_question_image"),
        path("list_all_questions/", list_all_questions, name="list_all_questions"), 
        path("get_question_by_subject_id/<int:subject_id>/", get_question_by_subject_id, name="get_question_by_subject_id"), 
        # path("get_test_by_subject_id/<int:subject_id>/", get_test_by_subject_id, name="get_test_by_subject_id"), 
        path("update_question/", update_question, name="update_question"),
        path("delete_question/", delete_question, name="delete_question"),
]