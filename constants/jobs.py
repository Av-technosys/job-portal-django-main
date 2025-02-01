JOB_TYPE_CHOICES = [
    (0, "Full Time"),
    (1, "Part Time"),
    (2, "Contract"),
]


JOB_LEVEL_CHOICES = [
    (0, "Beginner"),
    (1, "Intermediate"),
    (2, "Expert"),
]


JOB_STATUS_FIELDS = [
    (0, "Received"),
    (1, "In Review"),
    (2, "On Hold"),
    (3, "Shortlisted"),
    (4, "Interviewing"),
    (5, "Rejected"),
    (6, "Salary Negotiation"),
    (7, "Offered"),
    (8, "Joined"),
]

JOB_ROLE_FIELDS = [(0, "Developer"), (1, "Designer"), (2, "Manager")]
VALID_STATUS_TRANSITIONS = {
    0: [1, 2],  # Received → In Review, On Hold
    1: [3, 5],  # In Review → Shortlisted, Rejected
    2: [3, 4, 5],  # On Hold → Shortlisted, Interviewing, Rejected
    3: [4, 5],  # Shortlisted → Interviewing, Rejected
    4: [5, 6],  # Interviewing → Rejected, Salary Negotiation
    5: [],  # Rejected → No further transitions
    6: [7],  # Salary Negotiation → Offered
    7: [8],  # Offered → Joined
    8: [],  # Joined → No further transitions
}


JOB_SEEKER_LIST_VIEW_FIELDS = [
    "id",
    "title",
    "job_type",
    "location",
    "role",
    "company_name",
    "salary",
    "is_saved",
    "created_date",
    "company_profile_image",
]

SAVED_JOBS_JOB_SEEKER_LIST_VIEW_FIELDS = [
    "status",
    "id",
    "title",
    "job_type",
    "location",
    "role",
    "company_name",
    "salary",
    "is_applied",
    "created_date",
    "days_remaining",
    "company_profile_image",
]

JOB_APPLIED_VIEW_FIELDS = [
    "title",
    "location",
    "job_type",
    "salary",
    "applied_date",
    "job_id",
    "application_id",
    "company_profile_image",
    "role",
]

JOB_DESCRIPTION_SERIALIZER_FEILDS = [
    "education",
    "experience",
    "city",
    "state",
    "country",
    "skills",
    "description",
    "date_of_birth",
]

JOB_INFO_SERIALIZER_FEILDS = [
    "title",
    "role",
    "max_salary",
    "min_salary",
    "job_type",
    "job_level",
    "vacancies",
]

JOB_POSTED_VIEW_FEILDS = [
    "company_profile_image",
    "role",
    "title",
    "salary",
    "location",
    "job_type",
    "application_count",
    "job_id",
    "job_status",
]


JOB_POST_STATUS_FEILDS = [("active", "active"), ("expired", "expired")]


JOB_DETAILS_COMBINED_FIELDS = [
    "company_profile_image",
    "role",
    "company_name",
    "organization_type",
    "expired_at",
    "title",
    "salary",
    "job_type",
    "job_level",
    "vacancies",
    "education",
    "experience",
    "location",
    "skills",
    "description",
    "job_id",
    "job_status",
    "social_links",
    "created_date",
]

JOB_STATUS_UPDATED="Job Status Updated"