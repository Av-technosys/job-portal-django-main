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
    ("profile_image", "Profile Image"),
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
    "profile_image",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
    "created_date",
    "updated_date",
    "organization_type",
    "industry_type",
    "company_size",
    "company_website",
    "mission",
    "vision",
    "company_name",
]

COMBINE_STUDENT_PROFILE_FIELDS =  [
            "first_name", "email", "phone_number", "profile_image",
            "academic_qualifications", "work_experiences", "skill_sets",
            "certifications", "projects", "social_links"
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

JOB_SEEKER_PROFILE_GENERAL_INFO = [
    "qualification_type",
    "institution_name",
    "qualification_status",
    "score",
    "start_date",
    "end_date",
    "current_salary",
    "expected_salary",
    "job_search_status",
    "notice_period",
    "aq_id",
    "sy_id",
    "skill_sets",
    "files",
]

JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_1 = [
    "qualification_type",
    "institution_name",
    "qualification_status",
    "score",
    "start_date",
    "end_date",
]

JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_2 = [
    "id",
    "skill_name",
    "proficiency_level",
]

JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_3 = [
    "current_salary",
    "expected_salary",
    "job_search_status",
    "notice_period",
]

JOB_SEEKER_PROFILE_GENERAL_INFO_SUB_KEYS_4 = [
    "id",
    "file_type",
    "file",
]

JOB_SEEKER_PROFILE_ADDITIONAL_INFO = [
    "work_experiences",
    "certifications",
    "projects",
]

JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_1 = [
    "start_date",
    "end_date",
    "organization_name",
    "designation",
    "experience",
    "salary",
    "id",
]

JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_2 = [
    "start_date",
    "end_date",
    "certification_name",
    "institution_name",
    "id",
]

JOB_SEEKER_PROFILE_ADDITIONAL_INFO_SUB_KEYS_3 = [
    "start_date",
    "end_date",
    "project_name",
    "project_organization_name",
    "id",
]

# Industry options
INDUSTRY_CHOICES = [
    ("information_technology", "Information Technology"),
    ("healthcare", "Healthcare"),
    ("finance", "Finance"),
    ("education", "Education"),
    ("manufacturing", "Manufacturing"),
]

# Organization options
ORGANIZATION_CHOICES = [
    ("private", "Private"),
    ("public", "Public"),
    ("non_profit", "Non-Profit"),
    ("government", "Government"),
    ("start_up", "Start-up"),
]

# Company size options
COMPANY_SIZE_CHOICES = [
    ("1-10", "1-10"),
    ("11-50", "11-50"),
    ("51-200", "51-200"),
    ("201-500", "201-500"),
    ("501+", "501+"),
]

RECRUITER_PROFILE_PERSONAL_INFO = [
    "first_name",
    "company_about_us",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
    "recruiter_profile_id",
]


RECRUITER_PROFILE_PERSONAL_INFO_SUB_KEYS_1 = [
    "first_name",
]

RECRUITER_PROFILE_PERSONAL_INFO_SUB_KEYS_2 = [
    "company_about_us",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "postal_code",
    "country",
]

RECRUITER_PROFILE_FOUNDING_INFO = [
    "organization_type",
    "industry_type",
    "company_size",
    "company_website",
    "mission",
    "vision",
    "recruiter_founding_info_id",
    "files",
]


RECRUITER_PROFILE_FOUNDING_INFO_SUB_KEYS_1 = [
    "organization_type",
    "industry_type",
    "company_size",
    "company_website",
    "mission",
    "vision",
]

RECRUITER_PROFILE_FOUNDING_INFO_SUB_KEYS_2 = [
    "id",
    "file_type",
    "file",
]

RECRUITER_SOCIAL_LINKS = ["platform", "url", "id"]

JOB_SEEKER_SOCIAL_LINKS = ["platform", "url", "id"]


RECRUITER_DETAILS_FIELDS = ['first_name', 'industry_type', 'city', 'state', 'country', 'profile_image', 'user']

JOB_SEEKER_DETAILS_FIELDS = ["first_name", "profile_image", "city", "country", "id", "application_status", "experience", "application_id"]