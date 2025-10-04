"""Authentication routes"""
from flask import Blueprint, request, jsonify, g
from models import db, User
from auth import generate_token, verify_password, token_required
from services.audit_service import log_action

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint
    POST /api/login
    Body: { "email": "user@example.com", "password": "password123" }
    Returns: { "token": "jwt...", "user": {...} }
    """
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        email = data.get('email')
        password = data.get('password')

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403

        # Generate JWT token
        token = generate_token(user)

        # Log action
        log_action(user.id, 'USER_LOGIN', f'User {user.email} logged in')

        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """
    Logout endpoint
    POST /api/logout
    Headers: { "Authorization": "Bearer <token>" }
    Returns: { "success": true }
    """
    try:
        # Log action
        log_action(g.user_id, 'USER_LOGOUT', f'User logged out')

        return jsonify({'success': True}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        return jsonify({'error': str(e)}), 500
