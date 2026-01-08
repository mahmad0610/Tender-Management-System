import requests

API_URL = "http://localhost:8000"

users = [
    {"username": "admin", "password": "admin", "role": "admin", "email": "admin@example.com", "full_name": "System Administrator"},
    {"username": "technical", "password": "technical", "role": "technical", "email": "tech@example.com", "full_name": "Technical Lead"},
    {"username": "client", "password": "client", "role": "client", "email": "client@example.com", "full_name": "Main Client"},
    {"username": "vendor", "password": "vendor", "role": "vendor", "email": "vendor@example.com", "full_name": "Trusted Vendor"},
    {"username": "finance", "password": "finance", "role": "finance", "email": "finance@example.com", "full_name": "Finance Head"},
]

def seed_users():
    for user in users:
        try:
            res = requests.post(f"{API_URL}/users/", json=user)
            if res.status_code == 200:
                print(f"User {user['username']} created.")
            else:
                print(f"User {user['username']} already exists or failed: {res.text}")
        except Exception as e:
            print(f"Error creating user {user['username']}: {str(e)}")

if __name__ == "__main__":
    seed_users()
