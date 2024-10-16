from django.db import models
from django.conf import settings


# Model for basic job details (Section 1)
class JobInfo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # When a user is deleted, all associated jobs will also be deleted
    )
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.designation} at {self.department}"


# Model for job contact information (Section 2)
class JobContactInfo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Foreign key to the user table
    )
    job = models.OneToOneField(
        JobInfo, on_delete=models.CASCADE, related_name="contact_info"
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    job_description = models.TextField()
    skills_required = models.TextField()

    def __str__(self):
        return f"Contact for {self.job}: {self.name}"


# Model for job description and requirements (Section 3)
class JobDescription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Foreign key to the user table
    )
    job = models.OneToOneField(
        JobInfo, on_delete=models.CASCADE, related_name="description"  
    )

    job_overview = models.TextField()
    qualifications_and_skills = models.TextField()
    roles_and_responsibilities = models.TextField()

