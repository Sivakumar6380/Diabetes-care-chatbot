import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_dia_beat():
    print("--- DiaBeat AI Test Flow ---")
    
    # 1. Register
    email = f"diabeat_test_{int(time.time())}@example.com"
    print(f"Registering user: {email}...")
    reg_data = {"email": email, "name": "Diabetes Test User", "password": "password123"}
    response = requests.post(f"{BASE_URL}/register", json=reg_data)
    print("Register Response:", response.status_code)

    # 2. Login
    print("Logging in...")
    login_data = {"username": email, "password": "password123"}
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login Success!")

    # 3. Log Glucose
    print("\nLogging sugar level: 145 mg/dL (Post-meal)...")
    glucose_data = {"value": 145, "reading_type": "Post-meal"}
    response = requests.post(f"{BASE_URL}/glucose/", json=glucose_data, headers=headers)
    print("Glucose Logged:", response.json()["value"], "mg/dL")

    # 4. Fetch Latest
    print("Fetching latest reading...")
    response = requests.get(f"{BASE_URL}/glucose/latest", headers=headers)
    print("Latest Reading:", response.json()["value"])

    # 5. Chat about Diet
    print("\nUser: What should I eat for breakfast?")
    response = requests.post(f"{BASE_URL}/chat/", params={"message": "What should I eat for breakfast?"}, headers=headers)
    print("AI:", response.json()["response"])

    # 6. Chat about High Sugar
    print("\nUser: My sugar is 250, what should I do?")
    response = requests.post(f"{BASE_URL}/chat/", params={"message": "My sugar is 250, what should I do?"}, headers=headers)
    print("AI:", response.json()["response"])

    print("\n--- DiaBeat Test Flow Completed Successfully! ---")

if __name__ == "__main__":
    try:
        test_dia_beat()
    except Exception as e:
        print("Error:", e)
        print("Make sure the backend is running at http://127.0.0.1:8000")
