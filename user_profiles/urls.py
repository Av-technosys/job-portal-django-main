from django.urls import path
from .views import *

urlpatterns = [
    path("student_profile/", student_profile),
    path("qualifications/", academic_qualification),
    path("experience/", work_experience),
    path("skill_set/", skill_set),
    path("certifications/", certifications),
    path("projects/", projects),
    path("social_urls/", social_urls),
    path("social_urls_recruiter/", social_links_recruiter),

    path("company_profile/", company_profile),
    path('upload_recruiter/', upload_recruiters),
    path("job_details/", job_details),
    # path("company_id/", company_id),
    path("upload_document_recruiter/", file_upload_recruiter),
    path("upload_document_seeker/", file_upload_job_seeker),
    path("filter_job_seeker/", job_seeker),
    path("students_all_details/", students_all_details),
    path("application_status/", application_status),
    path("store_fcm_token/", store_fcm_token),
    path(
        "recruiter/<int:recruiter_id>/",
        get_recruiter_details,
        name="get_recruiter_by_id",
    ),
    path("list_recruiters/", get_recruiter, name="list_recruiter"),
]
