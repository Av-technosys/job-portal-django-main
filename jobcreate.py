import requests
import random
import string
from datetime import datetime, timedelta

# Base URL of your Django API
BASE_URL = "http://127.0.0.1:8000/jobs/"

# Authentication endpoint
AUTH_URL = "http://127.0.0.1:8000/accounts/login/"  

# Email-password list
CREDENTIALS = [
    "16qg7llz@example.com",
    "t9fclm9x@example.com",
    "rf8sn8y9@example.com",
    "ngd4lzqo@example.com",
    "ywggpjp5@example.com",
    "x7doo43k@example.com",
    "ig20hsh6@example.com",
    "d7gvlgks@example.com",
    "pk1s7eoq@example.com",
    "08hh0rqe@example.com",
    "o420shtt@example.com",
    "u00igt2t@example.com",
]
PASSWORD = "Admin@123"

# Function to authenticate user and return token
def authenticate_user(email, password):
    payload = {"email": email, "password": password}
    response = requests.post(AUTH_URL, json=payload)
    if response.status_code == 201:
        try:
            token = response.json().get("data", {}).get("token")
            if token:
                print(f"Authentication successful for {email}")
                return token
            else:
                print(f"Token not found in response for {email}: {response.json()}")
        except Exception as e:
            print(f"Error extracting token for {email}: {e}")
    else:
        print(f"Authentication failed for {email}: {response.status_code}, {response.text}")
    return None

# Function to generate random job post data
def generate_random_payload(base_payload):
    payload = base_payload.copy()
    
    # Randomize certain fields
    payload["title"] = random.choice([
        "Frontend Developer", "Backend Developer", "Full Stack Developer", "Software Engineer"
    ])
    payload["role"] = random.choice([
        "Frontend Developer", "Backend Developer", "Full Stack Developer"
    ])
    payload["max_salary"] = random.randint(90000, 150000)
    payload["min_salary"] = random.randint(60000, 90000)
    payload["job_type"] = random.choice(["Full-Time", "Part-Time", "Contract"])
    payload["job_level"] = random.choice(["Junior", "Mid-Level", "Senior"])
    payload["vacancies"] = random.randint(1, 10)
    payload["experience"] = random.randint(1, 5)
    payload["city"] = random.choice(["San Francisco", "New York", "Austin", "Seattle"])
    payload["state"] = random.choice(["California", "New York", "Texas", "Washington"])
    payload["date_of_birth"] = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
    payload["skills"] = random.sample(
        ["JavaScript", "React", "Node.js", "TypeScript", "Python", "Django", "CSS", "HTML", "Vue.js"],
        k=random.randint(3, 5)
    )
    payload["expiration_days"] = random.randint(7, 30)

    return payload

# Function to make POST requests for job posts
def create_jobs(token):
    base_payload = {
        "title": "Software Developer",
        "role": "Frontend Developer",
        "max_salary": 120000,
        "min_salary": 80000,
        "job_type": "Full-Time",
        "job_level": "Mid-Level",
        "vacancies": 3,
        "status": "active",
        "education": "Bachelor's Degree in Computer Science",
        "experience": 3,
        "city": "San Francisco",
        "date_of_birth": "2023-02-23",
        "state": "California",
        "country": "USA",
        "skills": ["JavaScript", "React", "HTML", "CSS", "TypeScript"],
        "description": "We are looking for talented developers to join our team.",
        "expiration_days": 10
    }

    headers = {"Authorization": f"token {token}"}

    for i in range(5):
        payload = generate_random_payload(base_payload)
        try:
            response = requests.post(BASE_URL + "job_details/", json=payload, headers=headers)
            if response.status_code == 201:
                print(f"Job {i + 1} created successfully.")
            else:
                print(f"Failed to create Job {i + 1}: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error creating Job {i + 1}: {e}")

# Function to authenticate and create job posts
def automate_job_posts():
    for email in CREDENTIALS:
        token = authenticate_user(email, PASSWORD)
        if token:
            create_jobs(token)

if __name__ == "__main__":
    automate_job_posts()
