import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_reminders():
    # 1. Register/Login
    email = f"tester_{int(time.time())}@diabeat.ai"
    password = "password123"
    
    print(f"Registering user: {email}")
    resp = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password, "name": "Tester"})
    print("Register Status:", resp.status_code)
    
    print("Logging in...")
    resp = requests.post(f"{BASE_URL}/token", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Manual Reminder Creation
    print("Creating manual reminder...")
    rem_data = {
        "reminder_type": "MEDICINE",
        "title": "Metformin",
        "dosage": "500mg",
        "reminder_time": "08:00",
        "frequency": "Daily",
        "meal_timing": "After Breakfast",
        "status": "Upcoming"
    }
    resp = requests.post(f"{BASE_URL}/reminders/", json=rem_data, headers=headers)
    print("Create Status:", resp.status_code)
    reminder_id = resp.json()["id"]
    print("Reminder ID:", reminder_id)
    
    # 3. Test GET Reminders
    print("Fetching reminders...")
    resp = requests.get(f"{BASE_URL}/reminders/", headers=headers)
    print("Reminders count:", len(resp.json()))
    
    # 4. Test PATCH status
    print("Updating reminder status to Completed...")
    resp = requests.patch(f"{BASE_URL}/reminders/{reminder_id}", json={"status": "Completed"}, headers=headers)
    print("Update Status:", resp.status_code)
    print("New Status:", resp.json()["status"])
    
    # 5. Test AI Chat Reminder Extraction
    print("Testing AI Chat reminder extraction...")
    chat_msg = "Remind me to drink water at 4 PM"
    resp = requests.post(f"{BASE_URL}/chat/?message={chat_msg}", headers=headers)
    chat_resp = resp.json()["response"]
    print("AI Response:", chat_resp)
    
    if "[REMINDER_ACTION:" in chat_resp:
        print("SUCCESS: AI detected reminder intent and added action tag.")
    else:
        print("WARNING: AI did not add action tag. Check prompt logic.")

if __name__ == "__main__":
    try:
        test_reminders()
    except Exception as e:
        print("Test failed:", e)
