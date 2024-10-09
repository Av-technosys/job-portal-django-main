from django.urls import path
from .views import section1_api_view, section2_api_view, section3_api_view

urlpatterns = [
    # Section 1
    path('job_section1/', section1_api_view, name='section1_post'),

    # Section 2
    path('job_section2/', section2_api_view, name='section2_post'),

    # Section 3
    path('job_section3/', section3_api_view, name='section3_post'),
]
