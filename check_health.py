import requests

API_URL = "http://localhost:8000"

def check_health():
    endpoints = ["/health", "/users/", "/tenders/"]
    for ep in endpoints:
        try:
            res = requests.get(f"{API_URL}{ep}")
            print(f"GET {ep}: {res.status_code}")
        except Exception as e:
            print(f"GET {ep}: FAILED - {e}")

if __name__ == "__main__":
    check_health()
