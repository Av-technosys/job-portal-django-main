from django.contrib import admin
from .models import (
    StudentProfile,
    AcademicQualification,
    WorkExperience,
    SkillSet,
    Certifications,
    Projects,
    SocialUrls,
    CompanyProfile,
    JobDetails,
    CompanyId,
    UploadedFile,
    FCMToken,
)

# Register your models here.
admin.site.register(StudentProfile)
admin.site.register(AcademicQualification)
admin.site.register(WorkExperience)
admin.site.register(SkillSet)
admin.site.register(Certifications)
admin.site.register(Projects)
admin.site.register(SocialUrls)
admin.site.register(CompanyProfile)
admin.site.register(JobDetails)
admin.site.register(CompanyId)
admin.site.register(UploadedFile)
admin.site.register(FCMToken)
