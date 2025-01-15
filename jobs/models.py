from django.db import models
from django.conf import settings
from constants.jobs import (
    JOB_STATUS_FIELDS,
    JOB_TYPE_CHOICES,
    JOB_LEVEL_CHOICES,
    JOB_ROLE_FIELDS,
    JOB_POST_STATUS_FEILDS,
)
from accounts.models import User
from django.contrib.postgres.fields import ArrayField


class JobInfo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ji_fk_user",
    )
    title = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=JOB_ROLE_FIELDS)
    max_salary = models.PositiveIntegerField()
    min_salary = models.PositiveIntegerField()
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    job_level = models.CharField(max_length=100, choices=JOB_LEVEL_CHOICES)
    vacancies = models.PositiveIntegerField()
    status = models.CharField(
        default=JOB_POST_STATUS_FEILDS[0][0], choices=JOB_POST_STATUS_FEILDS
    )
    expired_at = models.DateTimeField(null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["title"], name="job_info_title_index"),
            models.Index(fields=["job_type"], name="job_info_job_type_index"),
            models.Index(fields=["user"], name="job_info_user_index"),
            models.Index(fields=["created_date"], name="job_info_created_date_index"),
            models.Index(fields=["id", "user"], name="job_info_id_user_index"),
            # TBD Chore: Add Filter & Search Index
        ]

    def __str__(self):
        return self.title


class JobDescription(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jd_fk_user",
    )
    job = models.OneToOneField(
        JobInfo, on_delete=models.CASCADE, related_name="jd_fk_ji"
    )
    education = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    experience = models.PositiveIntegerField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    skills = ArrayField(models.CharField(max_length=200), size=10)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["job"], name="jd_job_index"),
            models.Index(fields=["user"], name="jd_user_index"),
            models.Index(fields=["created_date"], name="jd_created_date_index"),
            models.Index(fields=["id", "user"], name="jd_id_user_index"),
            # TBD Chore: Add Filter & Search Index
        ]

    def __str__(self):
        return self.education


class JobApply(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_id_applied"
    )
    job = models.ForeignKey(
        JobInfo, on_delete=models.CASCADE, related_name="job_id_applied"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_owner"
    )
    status = models.PositiveSmallIntegerField(choices=JOB_STATUS_FIELDS, default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application for {self.job.title} by {self.student.username}"

    class Meta:
        indexes = [
            models.Index(fields=["student"], name="job_apply_student_index"),
            models.Index(fields=["job"], name="job_apply_job_index"),
            models.Index(fields=["owner"], name="job_apply_owner_index"),
            models.Index(fields=["created_date"], name="job_apply_created_date_index"),
            models.Index(fields=["student", "job"], name="job_apply_student_job_index"),
            models.Index(fields=["job", "student"], name="job_apply_job_student_index"),
        ]


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

    class Meta:
        indexes = [
            models.Index(fields=["application"], name="comm_application_index"),
            models.Index(fields=["created_date"], name="comm_created_date_index"),
        ]

    def __str__(self):
        return f"Message from {self.sent_from.username} to {self.received_by.username}"


class JobSaved(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_id_saved"
    )
    job = models.ForeignKey(JobInfo, on_delete=models.CASCADE, related_name="saved_job")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"], name="job_saved_user_index"),
            models.Index(fields=["job"], name="job_saved_job_index"),
            models.Index(fields=["created_date"], name="job_saved_created_date_index"),
            models.Index(fields=["user", "job"], name="job_saved_user_job_index"),
            models.Index(fields=["job", "user"], name="job_saved_job_user_index"),
        ]


class CandidateSaved(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_id_saved"
    )
    job = models.ForeignKey(
        JobInfo, on_delete=models.CASCADE, related_name="job_id_saved"
    )
    recruiter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recruiter_id_saved"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["recruiter"], name="cs_recruiter_index"),
            models.Index(fields=["job"], name="cs_job_index"),
            models.Index(fields=["created_date"], name="cs_created_date_index"),
            models.Index(
                fields=["student", "recruiter"],
                name="cs_student_recruiter_index",
            ),
        ]
