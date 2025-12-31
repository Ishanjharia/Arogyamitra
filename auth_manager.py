import json
import os
import hashlib
import secrets
from datetime import datetime

DATA_DIR = "health_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def ensure_users_file():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)

def load_users():
    ensure_users_file()
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    ensure_users_file()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash, salt

def verify_password(password, stored_hash, salt):
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash

def create_user(name, email, password, role, language="English", phone=""):
    users = load_users()
    
    email_lower = email.lower().strip()
    if any(u['email'].lower() == email_lower for u in users):
        return {"success": False, "error": "Email already registered. Please sign in instead."}
    
    password_hash, salt = hash_password(password)
    
    user = {
        "id": len(users) + 1,
        "name": name.strip(),
        "email": email_lower,
        "password_hash": password_hash,
        "salt": salt,
        "role": role,
        "language": language,
        "phone": phone,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    users.append(user)
    save_users(users)
    
    safe_user = {k: v for k, v in user.items() if k not in ['password_hash', 'salt']}
    return {"success": True, "user": safe_user}

def authenticate_user(email, password):
    users = load_users()
    
    email_lower = email.lower().strip()
    user = None
    for u in users:
        if u['email'].lower() == email_lower:
            user = u
            break
    
    if not user:
        return {"success": False, "error": "Email not found. Please sign up first."}
    
    if not verify_password(password, user['password_hash'], user['salt']):
        return {"success": False, "error": "Incorrect password. Please try again."}
    
    user['last_login'] = datetime.now().isoformat()
    save_users(users)
    
    safe_user = {k: v for k, v in user.items() if k not in ['password_hash', 'salt']}
    return {"success": True, "user": safe_user}

def get_user_by_email(email):
    users = load_users()
    email_lower = email.lower().strip()
    
    for user in users:
        if user['email'].lower() == email_lower:
            safe_user = {k: v for k, v in user.items() if k not in ['password_hash', 'salt']}
            return safe_user
    
    return None

def update_user(user_id, **kwargs):
    users = load_users()
    
    for user in users:
        if user['id'] == user_id:
            for key, value in kwargs.items():
                if key not in ['password_hash', 'salt', 'id']:
                    user[key] = value
            save_users(users)
            safe_user = {k: v for k, v in user.items() if k not in ['password_hash', 'salt']}
            return {"success": True, "user": safe_user}
    
    return {"success": False, "error": "User not found"}

def change_password(user_id, old_password, new_password):
    users = load_users()
    
    for user in users:
        if user['id'] == user_id:
            if not verify_password(old_password, user['password_hash'], user['salt']):
                return {"success": False, "error": "Current password is incorrect"}
            
            new_hash, new_salt = hash_password(new_password)
            user['password_hash'] = new_hash
            user['salt'] = new_salt
            save_users(users)
            return {"success": True}
    
    return {"success": False, "error": "User not found"}

def get_all_users_by_role(role):
    users = load_users()
    filtered = []
    
    for user in users:
        if user['role'] == role:
            safe_user = {k: v for k, v in user.items() if k not in ['password_hash', 'salt']}
            filtered.append(safe_user)
    
    return filtered
