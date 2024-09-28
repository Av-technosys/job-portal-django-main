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
]
