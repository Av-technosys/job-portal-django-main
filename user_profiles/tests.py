from django.test import TestCase

from accounts.models import User
from user_profiles.models import OrganizationInfo, StudentProfile
from user_profiles.serializers import (
    AdminJobSeekerListSerializer,
    AdminRecruiterListSerializer,
)


class AdminUserListSerializerTests(TestCase):
    def test_job_seeker_list_includes_email_status_and_state(self):
        user = User.objects.create_user(
            username="jobseeker@example.com",
            email="jobseeker@example.com",
            first_name="Job Seeker",
            user_type=1,
            is_active=False,
        )
        StudentProfile.objects.create(
            user=user,
            date_of_birth="2000-01-01",
            gender=0,
            address_line_1="Line 1",
            city="Indore",
            state="Madhya Pradesh",
            postal_code=452001,
            country="India",
        )

        data = AdminJobSeekerListSerializer(user).data

        self.assertEqual(data["email"], "jobseeker@example.com")
        self.assertFalse(data["is_active"])
        self.assertEqual(data["status"], "Inactive")
        self.assertEqual(data["city"], "Indore")
        self.assertEqual(data["state"], "Madhya Pradesh")

    def test_recruiter_list_includes_email_status_city_and_state(self):
        user = User.objects.create_user(
            username="recruiter@example.com",
            email="recruiter@example.com",
            first_name="Recruiter",
            user_type=2,
            is_active=True,
        )
        OrganizationInfo.objects.create(
            user=user,
            company_about_us="About us",
            address_line_1="Line 1",
            city="Pune",
            state="Maharashtra",
            postal_code=411001,
            country="India",
        )

        data = AdminRecruiterListSerializer(user).data

        self.assertEqual(data["email"], "recruiter@example.com")
        self.assertTrue(data["is_active"])
        self.assertEqual(data["status"], "Active")
        self.assertEqual(data["city"], "Pune")
        self.assertEqual(data["state"], "Maharashtra")
