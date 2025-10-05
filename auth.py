"""Authentication and authorization middleware"""
from functools import wraps
from flask import request, jsonify, g
import jwt
import bcrypt
from datetime import datetime, timedelta
from config import Config
from models import User


def generate_token(user):
    """Generate JWT token for user with 8-hour expiration"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token


def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # Decode token
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            g.user_id = payload['user_id']
            g.user_role = payload['role']
            g.user_email = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated


def require_role(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        @token_required
        def wrapper(*args, **kwargs):
            if g.user_role not in allowed_roles:
                return jsonify({'error': 'Forbidden - insufficient permissions'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
