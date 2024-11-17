from rest_framework.permissions import BasePermission


class IsJobSeeker(BasePermission):
    """
    Permission for Job Seekers (Students).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 1


class IsRecruiter(BasePermission):
    """
    Permission for Recruiters.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 2


class IsJobSeekerOrRecruiter(BasePermission):
    """
    Permission for both Job Seekers and Recruiters.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [1, 2]
