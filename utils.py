import json
import os

PINS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pins.json")

def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def validate_password(password):
    import re
    if len(password) < 8:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

def is_duplicate_account(user_id, user_data):
    return user_id in user_data

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def load_pins():
    if not os.path.exists(PINS_FILE):
        return []
    with open(PINS_FILE, "r") as f:
        return json.load(f)

def save_pins(pins):
    os.makedirs(os.path.dirname(PINS_FILE), exist_ok=True)
    with open(PINS_FILE, "w") as f:
        json.dump(pins, f, indent=2)