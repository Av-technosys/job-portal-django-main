from django.urls import path
from  .views import *

urlpatterns = [
    path('student_profile/', student_profile),
    path('qualifications/', academic_qualification),
    path('experience/', work_experience ),
    path('skill_set/', skill_set),
    path('certifications/', certifications),
    path('projects/', projects),
    path('social_urls/', social_urls),
    path('get_student_profile/', get_student_profile),
    path('get_qualifications/', get_academic_qualification),
    path('get_experience/', get_work_experience ),
    path('get_skill_set/', get_skill_set),
    path('get_certifications/', get_certifications),
    path('get_projects/', get_projects),
    path('get_social_urls/', get_social_urls),
]
