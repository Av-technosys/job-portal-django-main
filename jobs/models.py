from django.db import models
from django.conf import settings
from constants.jobs import (
    JOB_STATUS_FIELDS,
    JOB_TYPE_CHOICES,
    JOB_LEVEL_CHOICES,
    JOB_ROLE_FIELDS,
    JOB_POST_STATUS_FEILDS
)
from django.db import models
from accounts.models import User


class JobInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=JOB_ROLE_FIELDS)
    max_salary = models.PositiveIntegerField()
    min_salary = models.PositiveIntegerField()
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    job_level = models.CharField(max_length=100, choices=JOB_LEVEL_CHOICES)
    vacancies = models.PositiveIntegerField()
    status = models.CharField(default=JOB_POST_STATUS_FEILDS[0][0], choices=JOB_POST_STATUS_FEILDS )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class JobDescription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(JobInfo, on_delete=models.CASCADE, related_name="job_descriptions")
    education = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    skills = models.TextField()
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.education


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
        User, on_delete=models.CASCADE, related_name="user_id_saved"
    )
    job = models.ForeignKey(JobInfo, on_delete=models.CASCADE, related_name="saved_job")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
