"""Authentication and authorization middleware"""
from functools import wraps
from flask import request, jsonify, g
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from config import Config
from models import User


def generate_token(user):
    """Generate JWT token for user with 8-hour expiration and JTI (JWT ID) for blacklisting"""
    jti = secrets.token_urlsafe(16)  # Unique token ID for blacklisting
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'jti': jti,  # JWT ID for token revocation
        'token_version': getattr(user, 'token_version', 0),  # Version for invalidation
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
    """Decorator to require valid JWT token with blacklist check"""
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

            # Check if token is blacklisted
            from security import is_token_blacklisted
            jti = payload.get('jti')
            if jti and is_token_blacklisted(jti):
                return jsonify({'error': 'Token has been revoked'}), 401

            # Check token version (for password changes)
            user = User.query.get(payload['user_id'])
            if user and hasattr(user, 'token_version'):
                if payload.get('token_version', 0) < user.token_version:
                    return jsonify({'error': 'Token has been invalidated'}), 401

            g.user_id = payload['user_id']
            g.user_role = payload['role']
            g.user_email = payload['email']
            g.token_jti = jti  # Store for potential blacklisting
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
