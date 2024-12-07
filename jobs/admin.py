from django.contrib import admin
from .models import (
    JobInfo,
    JobDescription,
    ContactAndSkills,
    JobOverviewAndQualifications,
    SkillsCertificationsResponsibilities,
    JobApply,
    Communication,
)

# Registering models in the admin panel
admin.site.register(JobInfo)
admin.site.register(JobDescription)
admin.site.register(ContactAndSkills)
admin.site.register(JobOverviewAndQualifications)
admin.site.register(SkillsCertificationsResponsibilities)
admin.site.register(JobApply)
admin.site.register(Communication)
