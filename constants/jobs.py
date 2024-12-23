JOB_DETAILS_FIELDS = [
    "id",
    "designation",
    "department",
    "location",
    "job_type",
    "job_description",
    "contact_and_skills",
    "job_overview_and_qualifications",
    "skills_certifications_responsibilities",
]

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


JOB_LIST_SEEKER_VIEW_FEILDS = [
    "id",
    "designation",
    "job_type",
    "location",
    "department",
    "company_name",
    "salary_range",
    "is_applied",
    "created_date",
    "company_profile_image",
]

JOB_APPLIED_VIEW_FEILDS = [
    "designation",
    "location",
    "job_type",
    "salary_range",
    "applied_date",
]
JOB_POSTED_VIEW_FEILDS = ["designation", "salary_range", "applicants_count", "location"]

JOB_DESCRIPTION_SERIALIZER_FEILDS = [
    "education",
    "experience",
    "city",
    "state",
    "country",
    "skills",
    "description",
]

JOB_INFO_SERIALIZER_FEILDS = [
    "title",
    "role",
    "max_salary",
    "min_salary",
    "job_type",
    "job_level",
    "vacancies",
    "job_id",
    "application_id" 
]

JOB_POSTED_VIEW_FEILDS = ["designation", "salary_range", "applicants_count", "location"]
