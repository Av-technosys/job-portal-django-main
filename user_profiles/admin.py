from django.contrib import admin
from .models import (
    StudentProfile,
    AcademicQualification,
    WorkExperience,
    SkillSet,
    Certifications,
    Projects,
    SocialUrls,
    OrganizationInfo,
    FoundingInfo,
    RecruiterUploadedFile,
    JobSeekerUploadedFile,
    SocialMediaLinkRecruiter,
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
admin.site.register(OrganizationInfo)
admin.site.register(FoundingInfo)
admin.site.register(JobSeekerUploadedFile)
admin.site.register(RecruiterUploadedFile)
admin.site.register(SocialMediaLinkRecruiter)
admin.site.register(FCMToken)
