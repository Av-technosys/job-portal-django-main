from django.db import models
from django.conf import settings
from constants.jobs import JOB_STATUS_FIELDS
from user_profiles.models import StudentProfile


from django.db import models


# Section 1: Job Details (Page 1)
class JobInfo(models.Model):
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    job_type = models.CharField(
        max_length=50,
        choices=[
            ("Full Time", "Full Time"),
            ("Part Time", "Part Time"),
            ("Contract", "Contract"),
        ],
    )
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
    company_name = models.CharField(max_length=100
                                    )
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


# Section 3: Job Overview, Academic Qualification, and Work Experience (Page 3)
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

    # Academic Qualification
    institution_name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Pursuing", "Pursuing"),
            ("Completed", "Completed"),
        ],
    )
    start_year = models.DateField()
    end_year = models.DateField()
    specialization = models.CharField(max_length=200)

    # Work Experience
    organization_name = models.CharField(max_length=200)
    designation_name = models.CharField(max_length=100)
    work_start_date = models.DateField()
    work_end_date = models.DateField()

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
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
class JobApply(models.Model):
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="students"
    )
    job = models.ForeignKey(
        JobInfo, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.PositiveSmallIntegerField(choices=JOB_STATUS_FIELDS, default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application for {self.job.designation} by {self.user}"