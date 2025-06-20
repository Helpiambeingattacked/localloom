import json
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_FILE = os.path.join(BASE_DIR, "data", "user.json")

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, 'r') as file:
        return json.load(file)

def save_users(users):
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)  # Ensure folder exists
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_password(password):
    return len(password) >= 6  # Example requirement: minimum 6 characters

def signup(account_id, password):
    users = load_users()
    if account_id in users:
        return "duplicate"  # Duplicate account ID
    if not is_valid_password(password):
        return "invalid_password"  # Invalid password
    users[account_id] = hash_password(password)
    save_users(users)
    return "success"

def login(account_id, password):
    users = load_users()
    hashed_password = hash_password(password)
    return users.get(account_id) == hashed_password