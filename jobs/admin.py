from django.contrib import admin
from .models import (
    JobDetails,
    JobDescription,
    ContactAndSkills,
    JobOverviewAndQualifications,
    SkillsCertificationsResponsibilities,
)

# Registering models in the admin panel
admin.site.register(JobDetails)
admin.site.register(JobDescription)
admin.site.register(ContactAndSkills)
admin.site.register(JobOverviewAndQualifications)
admin.site.register(SkillsCertificationsResponsibilities)
