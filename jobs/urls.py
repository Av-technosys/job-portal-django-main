from django.urls import path
from .views import (
    job_info_api_view,
    job_description_api_view,
    job_contact_info_api_view,
    get_job_details,
    apply_job
)

urlpatterns = [
    # Section 1
    path("job_info/", job_info_api_view, name="job_inf0_post"),
    # Section 2
    path("job_contact_info/", job_contact_info_api_view, name="job_contact_post"),
    # Section 3
    path("job_description/", job_description_api_view, name="job_description_post"),
    # Get all details by job id
    path("job_details/", get_job_details, name="get_job_details"),
    # Apply for job by student
    path("apply_job/", apply_job, name="apply_job"),
    
]
