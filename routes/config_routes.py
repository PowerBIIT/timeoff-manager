"""SMTP Configuration routes (Admin only)"""
from flask import Blueprint, request, jsonify, g
from models import db, SmtpConfig
from auth import require_role
from services.audit_service import log_action
from security import encrypt_password

config_bp = Blueprint('config', __name__)


@config_bp.route('/smtp-config', methods=['GET'])
@require_role('admin')
def get_smtp_config():
    """
    Get SMTP configuration (admin only)
    GET /api/smtp-config
    Headers: { "Authorization": "Bearer <token>" }
    Returns: {
        "server": "smtp.gmail.com",
        "port": 587,
        "use_ssl": true,
        "login": "system@firma.pl",
        "password": "***",
        "email_from": "system@firma.pl"
    }
    """
    try:
        config = SmtpConfig.query.first()

        if not config:
            # Return empty config if not set
            return jsonify({
                'server': None,
                'port': 587,
                'use_ssl': True,
                'login': None,
                'password': None,
                'email_from': None
            }), 200

        return jsonify(config.to_dict(mask_password=True)), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@config_bp.route('/smtp-config', methods=['POST'])
@require_role('admin')
def update_smtp_config():
    """
    Update SMTP configuration (admin only)
    POST /api/smtp-config
    Body: {
        "server": "smtp.gmail.com",
        "port": 587,
        "use_ssl": true,
        "login": "system@firma.pl",
        "password": "app_password",
        "email_from": "system@firma.pl"
    }
    Returns: { "success": true, "message": "Konfiguracja zapisana" }
    """
    try:
        data = request.get_json()

        # Get existing config or create new
        config = SmtpConfig.query.first()

        if not config:
            config = SmtpConfig()
            db.session.add(config)

        # Update fields if provided
        if 'server' in data:
            config.server = data['server']
        if 'port' in data:
            config.port = int(data['port'])
        if 'use_ssl' in data:
            config.use_ssl = data['use_ssl']
        if 'login' in data:
            config.login = data['login']
        if 'password' in data and data['password']:
            # Encrypt password before storing
            config.password = encrypt_password(data['password'])
        if 'email_from' in data:
            config.email_from = data['email_from']

        db.session.commit()

        # Log action
        log_action(
            g.user_id,
            'SMTP_CONFIG_UPDATED',
            f'Updated SMTP configuration - server: {config.server}'
        )

        return jsonify({
            'success': True,
            'message': 'Konfiguracja SMTP zapisana pomyślnie'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@config_bp.route('/smtp-config/test', methods=['POST'])
@require_role('admin')
def test_smtp_config():
    """
    Test SMTP configuration by sending a test email
    POST /api/smtp-config/test
    Body: { "test_email": "admin@firma.pl" }
    Returns: { "success": true, "message": "Test email sent" }
    """
    try:
        from services.email_service import send_email

        data = request.get_json()
        test_email = data.get('test_email')

        if not test_email:
            return jsonify({'error': 'test_email is required'}), 400

        # Send test email
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f8fafc; border-radius: 12px; padding: 40px;">
                <h2 style="color: #1e293b;">Test Email - TimeOff Manager</h2>
                <p style="color: #475569;">
                    This is a test email from your TimeOff Manager application.
                    If you received this, your SMTP configuration is working correctly!
                </p>
                <p style="color: #94a3b8; font-size: 12px; margin-top: 30px;">
                    Sent from TimeOff Manager
                </p>
            </div>
        </body>
        </html>
        """

        success, message = send_email(test_email, 'Test Email - TimeOff Manager', html_body)

        if success:
            # Log action
            log_action(
                g.user_id,
                'SMTP_TEST_SUCCESS',
                f'Sent test email to {test_email}'
            )
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@config_bp.route('/audit-logs', methods=['GET'])
@require_role('admin')
def get_audit_logs():
    """
    Get audit logs (admin only)
    GET /api/audit-logs?limit=50&user_id=5
    Headers: { "Authorization": "Bearer <token>" }
    Returns: [{ "id": 1, "user": "...", "action": "...", ... }]
    """
    try:
        from services.audit_service import get_audit_logs

        limit = int(request.args.get('limit', 100))
        user_id_filter = request.args.get('user_id')

        user_id = int(user_id_filter) if user_id_filter else None

        logs = get_audit_logs(limit=limit, user_id=user_id)

        return jsonify(logs), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
