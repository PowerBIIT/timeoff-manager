"""Production security enhancements"""
from functools import wraps
from flask import request, jsonify
import re
from cryptography.fernet import Fernet
import os
import base64
from hashlib import sha256


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password):
    """
    Validate password strength for production
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if len(password) < 8:
        return False, "Hasło musi mieć minimum 8 znaków"

    if not re.search(r'[A-Z]', password):
        return False, "Hasło musi zawierać przynajmniej jedną wielką literę"

    if not re.search(r'[a-z]', password):
        return False, "Hasło musi zawierać przynajmniej jedną małą literę"

    if not re.search(r'\d', password):
        return False, "Hasło musi zawierać przynajmniej jedną cyfrę"

    return True, "OK"


def rate_limit(max_requests=5, window_seconds=60):
    """
    Simple rate limiting decorator
    In production, use Redis-based rate limiting
    """
    requests_dict = {}

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            import time
            client_ip = request.remote_addr
            current_time = time.time()

            # Clean old entries
            requests_dict[client_ip] = [
                req_time for req_time in requests_dict.get(client_ip, [])
                if current_time - req_time < window_seconds
            ]

            # Check rate limit
            if len(requests_dict.get(client_ip, [])) >= max_requests:
                return jsonify({'error': 'Too many requests. Please try again later.'}), 429

            # Add current request
            if client_ip not in requests_dict:
                requests_dict[client_ip] = []
            requests_dict[client_ip].append(current_time)

            return f(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return text

    # Remove potential script tags and harmful HTML
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)

    return text.strip()


def validate_sql_injection(text):
    """Basic SQL injection detection"""
    if not text:
        return True

    # Suspicious patterns
    patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|\;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)"
    ]

    for pattern in patterns:
        if re.search(pattern, str(text), re.IGNORECASE):
            return False

    return True


def get_encryption_key():
    """
    Get or derive encryption key from SECRET_KEY
    Uses SHA256 to derive a valid Fernet key from SECRET_KEY
    """
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("SECRET_KEY must be set for encryption")

    # Derive a 32-byte key using SHA256
    key_bytes = sha256(secret_key.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_password(password):
    """
    Encrypt a password for secure storage

    Args:
        password: Plain text password to encrypt

    Returns:
        Encrypted password as string, or None if password is None/empty
    """
    if not password:
        return None

    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password):
    """
    Decrypt an encrypted password

    Args:
        encrypted_password: Encrypted password string

    Returns:
        Decrypted password as string, or None if input is None/empty
    """
    if not encrypted_password:
        return None

    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_password.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"⚠️  Failed to decrypt password: {str(e)}")
        return None
