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

# New Endpoints for Company
COMPANY_ENDPOINTS = {
    "company_details": "company_details/",
    "company_general": "company_general/",
    "upload_company_logo": "upload_company_logo/",
}

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


# Function to generate random company data
def generate_company_name():
    return random.choice(["Tech Corp", "Innovate Ltd", "Future Solutions"])

def generate_company_address():
    return "456, Business Avenue"

def generate_company_industry():
    return random.choice(["IT", "Finance", "Healthcare"])

def generate_company_size():
    return random.choice(["Small", "Medium", "Large"])

def generate_company_mission():
    return "To revolutionize the industry with cutting-edge solutions."

def generate_company_vision():
    return "To be a global leader in our sector."

# Function to make a POST request for company details
def post_company_details(token):
    payload = {
        "user_id": generate_user_id(),
        "company_name": generate_company_name(),
        "address_line_1": generate_company_address(),
        "address_line_2": generate_company_address(),
        "city": generate_city(),
        "state": generate_state(),
        "postal_code": generate_postal_code(),
        "country": generate_country(),
        "company_about_us": generate_company_mission(),
    }
    headers = {"Authorization": f"token {token}"}
    response = requests.post(BASE_URL + COMPANY_ENDPOINTS["company_details"], json=payload, headers=headers)
    if response.status_code == 201:
        print("Successfully posted company details:", response.json())
    else:
        print("Failed to post company details:", response.status_code, response.text)

# Function to make a POST request for general company information
def post_company_general_info(token):
    payload = {
        "user_id": generate_user_id(),
        "organization_type": random.choice(["Private", "Public"]),
        "industry_type": generate_company_industry(),
        "company_size": generate_company_size(),
        "company_website": f"https://{generate_company_name().lower().replace(' ', '')}.com",
        "mission": generate_company_mission(),
        "vision": generate_company_vision(),
    }
    headers = {"Authorization": f"token {token}"}
    response = requests.post(BASE_URL + COMPANY_ENDPOINTS["company_general"], json=payload, headers=headers)
    if response.status_code == 201:
        print("Successfully posted company general info:", response.json())
    else:
        print("Failed to post company general info:", response.status_code, response.text)

# Function to authenticate and loop through company accounts
def automate_company_data():
    for email in CREDENTIALS:
        token = authenticate_user(email, PASSWORD)
        if token:
            post_company_details(token)
            post_company_general_info(token)
