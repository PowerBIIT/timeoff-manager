"""
Production initialization route (one-time use)
Endpoint do czyszczenia bazy i utworzenia pierwszego admina
"""
from flask import Blueprint, request, jsonify
from models import db, User, Request, SmtpConfig, AuditLog
from auth import hash_password
from security import rate_limit, validate_password_strength
import os

init_bp = Blueprint('init', __name__)


@init_bp.route('/init-production', methods=['POST'])
@rate_limit(max_requests=3, window_seconds=3600)  # Only 3 attempts per hour
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
    - INIT_SECRET is set in environment
    - Correct INIT_SECRET is provided

    SECURITY: Remove INIT_SECRET from Azure config after first use to disable this endpoint!
    """
    try:
        # SECURITY: IP whitelist check (if configured)
        allowed_ips = os.getenv('INIT_ALLOWED_IPS', '').split(',')
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

        if allowed_ips and allowed_ips[0]:  # If whitelist is configured
            if client_ip not in allowed_ips:
                print(f"⚠️ SECURITY: INIT endpoint blocked from IP {client_ip}")
                return jsonify({'error': 'Access denied from this IP address'}), 403

        # SECURITY: Check if INIT_SECRET exists - if removed, endpoint is disabled
        init_secret = os.getenv('INIT_SECRET')
        if not init_secret:
            return jsonify({
                'error': 'Init endpoint is disabled. Remove INIT_SECRET from config to disable permanently.'
            }), 403

        # Check if any users exist (safety check - only allow on empty DB)
        user_count = User.query.count()

        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Verify secret (must be set in environment)
        if init_secret != data.get('secret'):
            print(f"⚠️ SECURITY: Invalid INIT_SECRET from IP {client_ip}")
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

        # Validate password strength (use new stronger validation)
        valid, message = validate_password_strength(admin_password)
        if not valid:
            return jsonify({'error': f'Password validation failed: {message}'}), 400

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
