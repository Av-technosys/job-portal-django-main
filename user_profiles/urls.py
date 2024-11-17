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
    path("company_profile/", company_profile),
    path("job_details/", job_details),
    path("company_id/", company_id),
    path("upload_document/", file_upload),
    path("filter_job_seeker/", job_seeker),
    path("students_all_details/", students_all_details),
    path("application_status/", application_status),
]
