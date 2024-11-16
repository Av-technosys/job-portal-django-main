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

JOB_TYPE_CHOICES = (
    [
        ("Full Time", "Full Time"),
        ("Part Time", "Part Time"),
        ("Contract", "Contract"),
    ],
)


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
