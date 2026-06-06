import requests
import json
import time
# Use timestamp to avoid duplicate username
username = f"user{int(time.time())}"
email = f"{username}@test.com"
password = "test123"
# Register
print("Registering...")
r = requests.post("http://127.0.0.1:8000/auth/register", json={
    "email": email,
    "username": username,
    "password": password
})
print(f"Register status: {r.status_code}")
if r.status_code == 201:
    print("✅ Registration successful")
    user_data = r.json()
    print(user_data)
else:
    print(f"Error: {r.text}")
    exit()
# Login
print("\nLogging in...")
r = requests.post("http://127.0.0.1:8000/auth/login", json={
    "username": username,
    "password": password
})
print(f"Login status: {r.status_code}")
if r.status_code == 200:
    print("✅ Login successful")
    print("Access token:", r.json()["access_token"][:50] + "...")
else:
    print(f"Error: {r.text}")
