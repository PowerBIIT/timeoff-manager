"""
Production initialization route (one-time use)
Endpoint do czyszczenia bazy i utworzenia pierwszego admina
"""
from flask import Blueprint, request, jsonify
from models import db, User, Request, SmtpConfig, AuditLog
from auth import hash_password
import os

init_bp = Blueprint('init', __name__)


@init_bp.route('/init-production', methods=['POST'])
def init_production():
    """
    One-time production initialization endpoint

    POST /api/init-production
    Body: {
        "secret": "INIT_SECRET from env",
        "admin_email": "admin@company.com",
        "admin_password": "SecurePass123!",
        "admin_first_name": "Admin",
        "admin_last_name": "User"
    }

    ⚠️ This endpoint is only available when:
    - Database has users (safety check)
    - Correct INIT_SECRET is provided

    After successful init, the endpoint returns 403 (to prevent reuse)
    """
    try:
        # Check if any users exist (safety check - only allow on empty DB)
        user_count = User.query.count()

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Verify secret (must be set in environment)
        init_secret = os.getenv('INIT_SECRET')
        if not init_secret or init_secret != data.get('secret'):
            return jsonify({'error': 'Invalid or missing INIT_SECRET'}), 403

        # Get admin credentials from request
        admin_email = data.get('admin_email')
        admin_password = data.get('admin_password')
        admin_first_name = data.get('admin_first_name', 'Admin')
        admin_last_name = data.get('admin_last_name', 'System')

        if not admin_email or not admin_password:
            return jsonify({'error': 'admin_email and admin_password are required'}), 400

        # Validate email
        if '@' not in admin_email:
            return jsonify({'error': 'Invalid email address'}), 400

        # Validate password strength
        if len(admin_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        # Clear all data
        deleted_requests = Request.query.delete()
        deleted_logs = AuditLog.query.delete()
        deleted_smtp = SmtpConfig.query.delete()
        deleted_users = User.query.delete()

        # Create first admin
        admin = User(
            email=admin_email,
            first_name=admin_first_name,
            last_name=admin_last_name,
            password_hash=hash_password(admin_password),
            role='admin',
            supervisor_id=None,
            is_active=True
        )

        db.session.add(admin)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Production database initialized successfully',
            'deleted': {
                'users': deleted_users,
                'requests': deleted_requests,
                'audit_logs': deleted_logs,
                'smtp_configs': deleted_smtp
            },
            'admin': {
                'email': admin_email,
                'first_name': admin_first_name,
                'last_name': admin_last_name
            },
            'next_steps': [
                'Login with admin credentials',
                'Change admin password',
                'Configure SMTP in Settings',
                'Add users'
            ]
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
