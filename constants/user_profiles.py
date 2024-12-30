GENDER_CHOICES = [
    (0, "Male"),
    (1, "Female"),
    (2, "Other"),
]

QUALIFICATION_STATUS = [
    (0, "Pursuing"),
    (1, "Completed"),
]

PROFICIENCY_LEVEL = [
    (0, "Beginner"),
    (1, "Intermediate"),
    (2, "Advanced"),
    (3, "Expert"),
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

JOB_SEEKER_DOCUMENT_TYPES = [
    ("resume", "Resume"),
    ("video_resume", "Video Resume"),
    ("certificate", "Certificate"),
    ("other", "Other"),
]

RECRUITER_DOCUMENT_TYPES = [
    ("organization_registration_number", "Organization Registration Number"),
    ("CIN_number", "CIN Number"),
    ("profile_image", "Profile Image"),
    ("GST_number", "GST Number"),
    ("other", "Other"),
]


NOTIFICATION_TYPE_CHOICES_ID = [0, 1]


NOTIFICATION_TYPE_CHOICES = [
    (NOTIFICATION_TYPE_CHOICES_ID[0], "new_job_application"),
    (NOTIFICATION_TYPE_CHOICES_ID[1], "job_application_communication"),
]

NOTIFICATION_TYPE_CHOICES_TITLE = {
    NOTIFICATION_TYPE_CHOICES_ID[0]: {
        "notification_title": "New Job Application Received",
        "notification_body": "A new submission is received from a student.",
    },
    NOTIFICATION_TYPE_CHOICES_ID[1]: {
        "notification_title": "Job Application Update",
        "notification_body": "A new message received",
    },
}

JOB_DETAILS_FIELDS = [
    "id",
    "user",
    "title",
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
    "salary",
    "uploaded_files",
]

COMPANY_PROFILE_FIELDS = [
    "id",
    "user",
    "company_about_us",
    "company_website",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
    "created_date",
    "updated_date",
    "company_id",
    "founding_info",
]

STUDENT_PROFILE_COMBINED_FIELDS = [
    "id",
    "user",
    "date_of_birth",
    "gender",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
    "created_date",
    "updated_date",
    "academic_qualifications",
    "work_experiences",
    "skill_sets",
    "certifications",
    "projects",
    "salary",
    "uploaded_files",
]


LIST_CANDIDATE_FEILDS = [
    "first_name",
    "id",
    "user",
    "designation",
    "city",
    "state",
    "country",
    "experience",
    "job_search_status",
]

JOB_SEEKER_PROFILE_PERSONAL_INFO = [
    "email",
    "first_name",
    "phone_number",
    "id",
    "date_of_birth",
    "gender",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
    "student_profile_id",
]

JOB_SEEKER_PROFILE_PERSONAL_INFO_SUB_KEYS_1 = [
    "first_name",
    "phone_number",
]

JOB_SEEKER_PROFILE_PERSONAL_INFO_SUB_KEYS_2 = [
    "date_of_birth",
    "gender",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
]

FIND_RECUITER_VIEW_FEILDS = [
    "user",
    "company_profile_image",
    "company_name",
    "organization_type",
    "industry_type",
    "city",
    "country",
    "created_date",
    "updated_date",
    "company_id",
]
