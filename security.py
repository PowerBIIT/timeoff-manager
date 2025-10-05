"""Production security enhancements"""
from functools import wraps
from flask import request, jsonify
import re
from cryptography.fernet import Fernet
import os
import base64
import time
from hashlib import sha256

# Redis-based rate limiting and token blacklist
try:
    import redis
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    redis_client = redis.from_url(redis_url, decode_responses=True)
    REDIS_AVAILABLE = True
    print(f"✅ Redis connected: {redis_url}")
except (ImportError, redis.exceptions.ConnectionError) as e:
    redis_client = None
    REDIS_AVAILABLE = False
    print(f"⚠️ WARNING: Redis not available - using in-memory fallback: {str(e)}")

# Fallback in-memory storage
_rate_limit_store = {}
_token_blacklist = set()


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password):
    """
    Validate password strength for production
    - Minimum 12 characters (zwiększone z 8)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 12:
        return False, "Hasło musi mieć minimum 12 znaków"

    if not re.search(r'[A-Z]', password):
        return False, "Hasło musi zawierać przynajmniej jedną wielką literę"

    if not re.search(r'[a-z]', password):
        return False, "Hasło musi zawierać przynajmniej jedną małą literę"

    if not re.search(r'\d', password):
        return False, "Hasło musi zawierać przynajmniej jedną cyfrę"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;\'`~]', password):
        return False, "Hasło musi zawierać przynajmniej jeden znak specjalny"

    return True, "OK"


def rate_limit(max_requests=5, window_seconds=60):
    """
    Rate limiting decorator with Redis support
    Fallback to in-memory if Redis unavailable
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

            if REDIS_AVAILABLE and redis_client:
                # Redis-based rate limiting (production-safe)
                key = f"rate_limit:{client_ip}:{f.__name__}"
                try:
                    current = redis_client.get(key)
                    if current and int(current) >= max_requests:
                        return jsonify({
                            'error': 'Too many requests. Please try again later.'
                        }), 429

                    pipe = redis_client.pipeline()
                    pipe.incr(key)
                    pipe.expire(key, window_seconds)
                    pipe.execute()
                except redis.exceptions.RedisError as e:
                    print(f"⚠️ Redis error in rate_limit: {str(e)}")
                    pass  # Allow request if Redis fails
            else:
                # Fallback in-memory rate limiting
                current_time = time.time()
                if client_ip not in _rate_limit_store:
                    _rate_limit_store[client_ip] = {}

                if f.__name__ not in _rate_limit_store[client_ip]:
                    _rate_limit_store[client_ip][f.__name__] = []

                _rate_limit_store[client_ip][f.__name__] = [
                    req_time for req_time in _rate_limit_store[client_ip][f.__name__]
                    if current_time - req_time < window_seconds
                ]

                if len(_rate_limit_store[client_ip][f.__name__]) >= max_requests:
                    return jsonify({
                        'error': 'Too many requests. Please try again later.'
                    }), 429

                _rate_limit_store[client_ip][f.__name__].append(current_time)

            return f(*args, **kwargs)
        return wrapper
    return decorator


def blacklist_token(jti, expiration_seconds=28800):
    """
    Add JWT token to blacklist (8 hours TTL)
    """
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.setex(f"blacklist:{jti}", expiration_seconds, "1")
            return True
        except redis.exceptions.RedisError as e:
            print(f"⚠️ Redis error in blacklist_token: {str(e)}")

    # Fallback in-memory blacklist
    _token_blacklist.add(jti)
    return False


def is_token_blacklisted(jti):
    """
    Check if token is blacklisted
    """
    if REDIS_AVAILABLE and redis_client:
        try:
            return redis_client.exists(f"blacklist:{jti}") > 0
        except redis.exceptions.RedisError as e:
            print(f"⚠️ Redis error in is_token_blacklisted: {str(e)}")
            return False

    # Fallback in-memory check
    return jti in _token_blacklist


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
