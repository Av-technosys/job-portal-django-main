from django.db import models
from django.conf import settings
from constants.jobs import JOB_STATUS_FIELDS, JOB_TYPE_CHOICES, SKILL_LEVEL_CHOICES
from user_profiles.models import StudentProfile


from django.db import models
from accounts.models import User


# Section 1: Job Details (Page 1)
class JobInfo(models.Model):
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    description = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.designation} - {self.department}"


# Section 2: Job Description (Page 2)
class JobDescription(models.Model):
    job = models.ForeignKey(
        JobInfo, on_delete=models.CASCADE, related_name="job_description"
    )
    job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):

        return f"{self.job_title} at {self.company_name}"


# Section 2: Contact and Skills (Page 2)
class ContactAndSkills(models.Model):
    job = models.ForeignKey(
        JobInfo, on_delete=models.CASCADE, related_name="contact_and_skills"
    )

    # Contact Information
    full_name = models.CharField(max_length=100)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    # Skills
    skills_required = models.TextField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.full_name


# Section 3: Job Overview (Page 3)
class JobOverviewAndQualifications(models.Model):
    job = models.ForeignKey(
        JobInfo,
        on_delete=models.CASCADE,
        related_name="job_overview_and_qualifications",
    )

    # Job Overview
    job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    salary_range = models.CharField(max_length=100, blank=True, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Foreign key to the user table
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


# Section 3: Skills, Roles & Responsibilities (Page 3)
class SkillsCertificationsResponsibilities(models.Model):
    job = models.ForeignKey(
        JobInfo,
        on_delete=models.CASCADE,
        related_name="skills_certifications_responsibilities",
    )

    # Skills
    skill_name = models.CharField(max_length=100)
    skill_level = models.CharField(
        max_length=50,
        choices=SKILL_LEVEL_CHOICES,
        blank=True,
        null=True,
    )
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)

    # Roles and Responsibilities
    job_role = models.CharField(max_length=100)
    responsibilities = models.TextField(max_length=500)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.job_role} - {self.certificate_name if self.certificate_name else 'No Certificate'}"


class JobApply(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_id_applied"
    )
    job = models.ForeignKey(
        JobInfo, on_delete=models.CASCADE, related_name="applications"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_owner"
    )
    status = models.PositiveSmallIntegerField(choices=JOB_STATUS_FIELDS, default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application for {self.job.designation} by {self.student.username}"


class Communication(models.Model):
    application = models.ForeignKey(
        JobApply, on_delete=models.CASCADE, related_name="communication_id"
    )
    message = models.TextField()
    sent_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_sent_from",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_received_by",
    )
    meta_data = models.JSONField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sent_from.username} to {self.received_by.username}"


class JobSaved(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_id_saaved"
    )
    job = models.ForeignKey(JobInfo, on_delete=models.CASCADE, related_name="saved_job")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
