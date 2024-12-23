from django.contrib import admin
from .models import (
    JobInfo,
    JobDescription,
    JobApply,
    Communication,
)

# Registering models in the admin panel
admin.site.register(JobInfo)
admin.site.register(JobDescription)
admin.site.register(JobApply)
admin.site.register(Communication)
