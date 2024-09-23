from django.urls import path
from  .views import *

urlpatterns = [
    path('student_profile/', student_profile),
    path('section_one/', academic_qualification),
    path('section_two/', work_experience ),
    path('section_three/', skill_set),
    path('section_four/', certifications),
    path('section_five/', projects),
    path('section_six/', social_urls),
    path('get_student_profile/', get_student_profile),
    path('get_section_one/', get_academic_qualification),
    path('get_section_two/', get_work_experience ),
    path('get_section_three/', get_skill_set),
    path('get_section_four/', get_certifications),
    path('get_section_five/', get_projects),
    path('get_section_six/', get_social_urls),
]
