from django.urls import path
from .views import *

urlpatterns = [
    # Section 1: JobDetails
    path("job_details/", job_details_api_view, name="job_details_post"),
    
   
    # Apply for job by student
    path("apply_job/", apply_job, name="apply_job"),
    # API for job list
    path("list_jobs/", list_jobs, name="list_jobs"),
    # API for my posted job list
    path("my_posted_jobs/", my_posted_jobs, name="my_posted_jobs"),
    # get all the submitted application by the student to recruiter
    path(
        "submitted_jobs_application/",
        submitted_jobs_application,
        name="submitted_jobs_application",
    ),
    # get all submitted jobs by student ----- pyload = { _id : }
    path("list_submitted_jobs/", list_submitted_jobs, name="list_submitted_jobs"),
    # get application status
    path("application_status/", application_status, name="application_status"),
    # chat
    path("chat/<int:application_id>", chat, name="chat"),
    # save,delete and get saved jobs
    path("save_job/", save_job, name="save_job"),
    path("summary/", summary_view, name="summary_view"),
]
