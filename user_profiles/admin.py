from django.contrib import admin
from .models import (
    AcademicQualification,
    Certifications,
    FCMToken,
    FoundingInfo,
    JobSeekerUploadedFile,
    OrganizationInfo,
    Projects,
    RecruiterUploadedFile,
    Salary,
    SkillSet,
    SocialMediaLinkJobSeeker,
    SocialMediaLinkRecruiter,
    StudentProfile,
    WorkExperience,
)

# Register your models here.
admin.site.register(StudentProfile)
admin.site.register(AcademicQualification)
admin.site.register(WorkExperience)
admin.site.register(SkillSet)
admin.site.register(Certifications)
admin.site.register(Projects)
admin.site.register(Salary)
admin.site.register(OrganizationInfo)
admin.site.register(FoundingInfo)
admin.site.register(JobSeekerUploadedFile)
admin.site.register(RecruiterUploadedFile)
admin.site.register(SocialMediaLinkRecruiter)
admin.site.register(SocialMediaLinkJobSeeker)
admin.site.register(FCMToken)
