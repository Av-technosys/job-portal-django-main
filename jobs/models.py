from django.db import models
from django.conf import settings


class Jobs(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # Section 1 fields
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    # Section 2 fields
    job_description = models.TextField()
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    skills_required = models.TextField()

    # Section 3 fields
    job_overview = models.TextField()
    qualifications_and_skills = models.TextField()
    roles_and_responsibilities = models.TextField()
