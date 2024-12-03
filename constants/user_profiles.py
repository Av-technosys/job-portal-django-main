GENDER_CHOICES = [
    (0, "Male"),
    (1, "Female"),
    (2, "Other"),
]

NOTICE_PERIOD_CHOICES = [
    (0, "Immediately"),
    (1, "15 days"),
    (2, "30 days"),
    (3, "30+ days"),
]

SEARCH_STATUS_CHOICES = [
    (0, "Actively Looking"),
    (1, "Passively Looking"),
    (2, "Not Looking"),
]

JOB_TYPE_CHOICES = [
    (0, "Internship"),
    (1, "Part Time"),
    (2, "Full Time"),
]

DOCUMENT_TYPES = [
    ("resume", "Resume"),
    ("cover_letter", "Cover Letter"),
    ("profile_image", "Profile Image"),
    ("typescript", "Typescript"),
]

NOTIFICATION_TYPE_CHOICES_ID = [0]


NOTIFICATION_TYPE_CHOICES = [
    (NOTIFICATION_TYPE_CHOICES_ID[0], "new_job_application"),
]

NOTIFICATION_TYPE_CHOICES_TITLE = {
    NOTIFICATION_TYPE_CHOICES_ID[0]: {
        "notification_title": "New Job Application Received",
        "notification_body": "A new submission is received from a student.",
    },
}

JOB_DETAILS_FIELDS = [
    "id",
    "user",
    "designation",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
    "experience",
    "gender",
    "current_salary",
    "expecting_salary",
    "job_search_status",
    "interests",
    "notice_period",
    "short_bio",
    "updated_date",
    "academic_qualifications",
    "work_experiences",
    "skill_sets",
    "certifications",
    "projects",
    "social_urls",
    "uploaded_files",
]
