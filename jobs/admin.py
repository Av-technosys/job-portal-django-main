from django.contrib import admin
from .models import (
    Job,
    JobDescription,
    JobApply,
    Communication,
)

# Registering models in the admin panel
admin.site.register(Job)
admin.site.register(JobDescription)
admin.site.register(JobApply)
admin.site.register(Communication)
