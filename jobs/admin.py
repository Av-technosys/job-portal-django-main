from django.contrib import admin
from .models import JobContactInfo, JobDescription, JobInfo

# Register your models here.

admin.site.register(JobInfo)
admin.site.register(JobDescription)
admin.site.register(JobContactInfo)
