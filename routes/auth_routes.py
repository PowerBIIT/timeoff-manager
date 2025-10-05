"""Authentication routes"""
from flask import Blueprint, request, jsonify, g
from models import db, User
from auth import generate_token, verify_password, token_required
from services.audit_service import log_action
from security import rate_limit, validate_email, blacklist_token
import time

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes (stricter)
def login():
    """
    Login endpoint with constant-time response (timing attack prevention)
    POST /api/login
    Body: { "email": "user@example.com", "password": "password123" }
    Returns: { "token": "jwt...", "user": {...} }
    """
    start_time = time.time()
    response_data = None
    status_code = 401

    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            response_data = {'error': 'Email and password are required'}
            status_code = 400
        else:
            email = data.get('email')
            password = data.get('password')

            # Validate email format
            if not validate_email(email):
                response_data = {'error': 'Invalid email format'}
                status_code = 400
            else:
                # Find user by email
                user = User.query.filter_by(email=email).first()

                # Always verify password (even if user doesn't exist) for constant-time
                if user:
                    password_valid = verify_password(password, user.password_hash)
                else:
                    # Dummy password check to prevent timing attack
                    from auth import hash_password
                    dummy_hash = hash_password("dummy_password_for_timing")
                    verify_password(password, dummy_hash)
                    password_valid = False

                if not user or not password_valid:
                    response_data = {'error': 'Invalid email or password'}
                    status_code = 401
                elif not user.is_active:
                    response_data = {'error': 'Account is disabled'}
                    status_code = 403
                else:
                    # Success - Generate JWT token
                    token = generate_token(user)

                    # Log action (non-blocking)
                    try:
                        log_action(user.id, 'USER_LOGIN', f'User {user.email} logged in')
                    except:
                        pass

                    response_data = {
                        'token': token,
                        'user': user.to_dict()
                    }
                    status_code = 200

    except Exception as e:
        import logging
        logging.error(f"Login error: {str(e)}", exc_info=True)
        response_data = {'error': 'Internal server error'}
        status_code = 500

    # Constant-time response - always wait at least 200ms
    elapsed = time.time() - start_time
    if elapsed < 0.2:
        time.sleep(0.2 - elapsed)

    return jsonify(response_data), status_code


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Logout endpoint - blacklists current token
    POST /api/logout
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "success": true }
    """
    try:
        # Blacklist current token (if JTI available)
        if hasattr(g, 'token_jti') and g.token_jti:
            blacklist_token(g.token_jti)

        # Log action
        log_action(g.user_id, 'USER_LOGOUT', f'User logged out')

        return jsonify({'success': True}), 200

    except Exception as e:
        import logging
        logging.error(f"Logout error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Get current user information
    GET /api/me
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "id": 1, "email": "...", "first_name": "...", ... }
    """
    try:
        user = User.query.get(g.user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200

    except Exception as e:
        import logging
        logging.error(f"Get current user error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
