import requests
import random
import string

# Base URL of your Django API
BASE_URL = "http://127.0.0.1:8000/user_profiles/"

# Authentication endpoint
AUTH_URL = "http://127.0.0.1:8000/accounts/login/"  # Replace with your actual login endpoint

# URL endpoints
ENDPOINTS = {
    "job_seeker_personal": "job_seeker_personal/",
    "job_seeker_general": "job_seeker_general/",
    "upload_profile_image": "upload_profile_image/",
}

# Email-password list
CREDENTIALS = [
    "gzy261o6@example.com",
    "4ydl1zps@example.com",
    "34ee63e6@example.com",
    "m03yazmb@example.com",
    "ychkwuqo@example.com",
    "lg0vssy@example.com",
    "5y38sg7e@example.com",
    "iat2t0oq@example.com",
    "9n9tawbx@example.com",
    "mp8m7k3i@example.com",
]
PASSWORD = "Admin@123"

# Choices for different fields
GENDER_CHOICES = [0, 1, 2]
QUALIFICATION_STATUS = [0, 1]
PROFICIENCY_LEVEL = [0, 1, 2, 3]
NOTICE_PERIOD_CHOICES = [0, 1, 2, 3]
SEARCH_STATUS_CHOICES = [0, 1, 2]
JOB_TYPE_CHOICES = [0, 1, 2]

# Function to authenticate and get a token
def authenticate_user(email, password):
    payload = {"email": email, "password": password}
    response = requests.post(AUTH_URL, json=payload)
    if response.status_code == 201:
        try:
            # Extract the token from the nested structure
            token = response.json().get("data", {}).get("token")
            if token:
                return token
            else:
                print(f"Token not found in response for {email}: {response.json()}")
                return None
        except Exception as e:
            print(f"Error extracting token for {email}: {e}")
            return None
    else:
        print(f"Authentication failed for {email}: {response.status_code}, {response.text}")
        return None


# Function to generate random data
def generate_user_id():
    return random.randint(156, 178)

def generate_date_of_birth():
    return "1995-05-20"  # Example DOB

def generate_gender():
    return random.choice(GENDER_CHOICES)

def generate_address():
    return "123, Random Street"

def generate_city():
    return random.choice(["New York", "Los Angeles", "Chicago"])

def generate_state():
    return random.choice(["NY", "CA", "IL"])

def generate_postal_code():
    return ''.join(random.choices(string.digits, k=6))

def generate_country():
    return random.choice(["USA", "Canada", "UK"])

def generate_qualification_status():
    return random.choice(QUALIFICATION_STATUS)

# Function to make a POST request for personal details
def post_job_seeker_personal_details(token):
    payload = {
        "first_name" : "Dilip",
        "user_id": generate_user_id(),
        "date_of_birth": generate_date_of_birth(),
        "gender": generate_gender(),
        "phone_number" : 1234567780,
        "address_line_1": generate_address(),
        "address_line_2" : generate_address(),
        "city": generate_city(),
        "state": generate_state(),
        "postal_code": generate_postal_code(),
        "country": generate_country(),
    }
    headers = {"Authorization": f"token {token}"}
    response = requests.post(BASE_URL + ENDPOINTS["job_seeker_personal"], json=payload, headers=headers)
    if response.status_code == 201:
        print("Successfully posted job seeker personal details:", response.json())
    else:
        print("Failed to post job seeker personal details:", response.status_code, response.text)

# Function to make a POST request for general details
def post_job_seeker_general_details(token):
    payload = {
        "user_id": generate_user_id(),
        "qualification_type": random.choice(["Bachelor's", "Master's", "PhD"]),
        "institution_name": "Random University",
        "qualification_status": generate_qualification_status(),
        "score": round(random.uniform(2.0, 4.0), 2),
        "start_date": "2015-08-15",
        "end_date" : "2015-08-19",
        "skill_sets":[{"skill_name": "Go", "proficiency_level": 3}],
        "job_search_status" : 0,
        "current_salary" : 100,
        "expected_salary" : 200,
        "notice_period" : 0
    }
    headers = {"Authorization": f"token {token}"}
    response = requests.post(BASE_URL + ENDPOINTS["job_seeker_general"], json=payload, headers=headers)
    if response.status_code == 201:
        print("Successfully posted job seeker general details:", response.json())
    else:
        print("Failed to post job seeker general details:", response.status_code, response.text)

# Main function to process multiple users
def create_multiple_requests():
    for email in CREDENTIALS:
        token = authenticate_user(email, PASSWORD)
        if token:
            print(f"Authenticated successfully for {email}. Token: {token}")
            post_job_seeker_personal_details(token)
            post_job_seeker_general_details(token)
        else:
            print(f"Skipping user {email} due to failed authentication.")

# Main execution
if __name__ == "__main__":
    create_multiple_requests()
