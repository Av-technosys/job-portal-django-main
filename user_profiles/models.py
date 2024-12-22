from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from constants.user_profiles import *
from functions.common import file_rename
from storages.backends.s3boto3 import S3Boto3Storage


class S3FileStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StudentProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    designation = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.IntegerField(validators=[MaxValueValidator(999999)])
    country = models.CharField(max_length=100)
    experience = models.PositiveSmallIntegerField(validators=[MaxValueValidator(99)])
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2)
    expecting_salary = models.DecimalField(max_digits=10, decimal_places=2)
    job_search_status = models.PositiveSmallIntegerField(choices=SEARCH_STATUS_CHOICES)
    interests = models.TextField(blank=True, null=True, max_length=400)
    notice_period = models.PositiveSmallIntegerField(choices=NOTICE_PERIOD_CHOICES)
    short_bio = models.TextField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.short_bio} - {self.designation}"


class AcademicQualification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="academic_qualifications",
    )
    institution_name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.institution_name} - {self.specialization}"


class WorkExperience(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="work_experiences",
    )
    organization_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization_name} - {self.designation}"


class SkillSet(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="skill_sets",
    )
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=50)
    experience = models.PositiveIntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.skill_name}"


class Certifications(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="certifications",
    )
    certification_name = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    certificate_url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.certification_name}"


class Projects(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    project_name = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project_name} - {self.user}"


class SocialUrls(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="social_urls",
    )
    link = models.URLField(blank=True)
    link_title = models.CharField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.link} - {self.link_title}"


class OrganizationInfo(models.Model):
    id = models.AutoField(primary_key=True)
    user = (
        models.OneToOneField(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name="organizations_info",
        ),
    )
    company_about_us = models.TextField(max_length=500)
    # company_url = models.URLField(blank=True)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.IntegerField(validators=[MaxValueValidator(999999)])
    country = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class FoundingInfo(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="founding_info"
    )
    organization_type = models.CharField(max_length=200)
    industry_type = models.CharField(max_length=200)
    company_size = models.PositiveSmallIntegerField()
    company_website = models.CharField(max_length=300)
    mission = models.TextField(null=True, blank=True)
    vision = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

class SocialMediaLink(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_media_links",
    )
    id = models.AutoField(primary_key=True)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_platform_display()} - {self.url}"

class JobRecruiterUploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    file_type = models.CharField(max_length=50, choices=JOB_RECRUITER_DOCUMENT_TYPES)
    file = models.FileField(upload_to=file_rename, storage=S3FileStorage())
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_type} for user {self.user.username}"


class JobSeekerUploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    file_type = models.CharField(max_length=50, choices=JOB_SEEKER_DOCUMENT_TYPES)
    file = models.FileField(upload_to=file_rename, storage=S3FileStorage())
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file_type} for user {self.user.username}"


class FCMToken(models.Model):
    id = models.AutoField(primary_key=True)
    fcm_token = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"FCM token for {self.user.username}"
