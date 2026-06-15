from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from functions.cache import invalidate_response_cache_namespace
from jobs.models import JobDescription, JobInfo


def _invalidate_job_list_cache():
    transaction.on_commit(lambda: invalidate_response_cache_namespace("list_jobs"))


@receiver(post_save, sender=JobInfo, dispatch_uid="invalidate_list_jobs_on_job_save")
@receiver(post_delete, sender=JobInfo, dispatch_uid="invalidate_list_jobs_on_job_delete")
@receiver(
    post_save,
    sender=JobDescription,
    dispatch_uid="invalidate_list_jobs_on_job_description_save",
)
@receiver(
    post_delete,
    sender=JobDescription,
    dispatch_uid="invalidate_list_jobs_on_job_description_delete",
)
def invalidate_list_jobs_cache(**kwargs):
    _invalidate_job_list_cache()
