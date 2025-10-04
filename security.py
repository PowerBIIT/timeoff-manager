"""Production security enhancements"""
from functools import wraps
from flask import request, jsonify
import re


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
