from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from functions.cache import invalidate_response_cache_namespaces
from user_profiles.models import FoundingInfo, OrganizationInfo, RecruiterUploadedFile


def _invalidate_recruiter_cache():
    transaction.on_commit(
        lambda: invalidate_response_cache_namespaces("list_recruiters", "list_jobs")
    )


@receiver(
    post_save,
    sender=OrganizationInfo,
    dispatch_uid="invalidate_recruiter_cache_on_organization_save",
)
@receiver(
    post_delete,
    sender=OrganizationInfo,
    dispatch_uid="invalidate_recruiter_cache_on_organization_delete",
)
@receiver(
    post_save,
    sender=FoundingInfo,
    dispatch_uid="invalidate_recruiter_cache_on_founding_save",
)
@receiver(
    post_delete,
    sender=FoundingInfo,
    dispatch_uid="invalidate_recruiter_cache_on_founding_delete",
)
@receiver(
    post_save,
    sender=RecruiterUploadedFile,
    dispatch_uid="invalidate_recruiter_cache_on_file_save",
)
@receiver(
    post_delete,
    sender=RecruiterUploadedFile,
    dispatch_uid="invalidate_recruiter_cache_on_file_delete",
)
def invalidate_recruiter_cache(**kwargs):
    _invalidate_recruiter_cache()
