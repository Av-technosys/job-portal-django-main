from django.urls import path
from .views import (
    job_info_api_view,
    job_description_api_view,
    job_contact_info_api_view,
)

urlpatterns = [
    # Section 1
    path("job_info/", job_info_api_view, name="job_inf0_post"),
    # Section 2
    path("job_contact_info/", job_contact_info_api_view, name="job_contact_post"),
    # Section 3
    path("job_description/", job_description_api_view, name="job_description_post"),
]
