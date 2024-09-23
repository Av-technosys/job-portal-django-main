STUDENT_PROFILE_FIELDS = [
            'id','user','first_name', 'last_name', 'designation', 
            'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 
            'country', 'experience', 'gender', 'current_salary', 'expecting_salary',
            'job_search_status', 'interests', 'notice_period', 'short_bio'
        ]

ACADEMIC_QUALIFICATION_FIELDS = [
            'id', 'user', 'institution_name', 'start_year', 
            'end_year', 'degree_status', 'specialization'
        ]

WORK_EXPERIENCE_FIELD =  [
            'id', 'user', 'organization_name', 'designation', 
            'start_date', 'end_date'
        ]

SKILL_SET_FIELD =  [
            'id', 'user', 'skill_name', 'proficiency_level', 'experience'
        ]

CERTIFICATIONS_FIEDL = [
            'id', 'user', 'certification_name', 'start_date', 
            'end_date', 'certificate_url'
        ]

PROJECT_FIELD = [
            'id', 'user', 'project_name', 'description', 'project_url'
        ]



SOCIAL_FIEDL =  [
            'id', 'user', 'link','link_title'
        ]

GENDER_CHOICES = [
        (0, 'Male'),
        (1, 'Female'),
        (2, 'Other'),
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