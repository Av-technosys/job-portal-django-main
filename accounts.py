import requests
import random
import string

# URL of the API endpoint
API_URL = "http://127.0.0.1:8000/accounts/register/"

# Function to generate random data
def generate_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + "@example.com"

def generate_first_name():
    return random.choice(["John", "Jane", "Alex", "Emily", "Chris", "Anna"])

def generate_password():
    return "Admin@123"

def generate_phone_number():
    return ''.join(random.choices(string.digits, k=10))

def generate_user_type():
    return random.choice([2])

# Function to create a user
def create_user():
    email = generate_email()
    first_name = generate_first_name()
    password = generate_password()
    phone_number = generate_phone_number()
    user_type = generate_user_type()

    payload = {
        "email": email,
        "first_name": first_name,
        "password": password,
        "phone_number": phone_number,
        "user_type": user_type
    }

    response = requests.post(API_URL, json=payload)

    if response.status_code == 201:
        print(f"Successfully created user: {email}")
    else:
        print(f"Failed to create user: {response.status_code}, {response.text}")

# Create multiple users
def create_multiple_users(count):
    for _ in range(count):
        create_user()

if __name__ == "__main__":
    user_count = int(input("Enter the number of users to create: "))
    create_multiple_users(user_count)
