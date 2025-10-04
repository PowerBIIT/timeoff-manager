"""Audit logging service"""
from models import db, AuditLog
from datetime import datetime


def log_action(user_id, action, details=None):
    """
    Log an action to the audit log

    Args:
        user_id: ID of the user performing the action (can be None for system actions)
        action: Description of the action (e.g., "USER_CREATED", "REQUEST_APPROVED")
        details: Optional additional details as string
    """
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.session.add(audit_entry)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error logging audit action: {str(e)}")
        db.session.rollback()
        return False


def get_audit_logs(limit=100, user_id=None):
    """
    Retrieve audit logs

    Args:
        limit: Maximum number of logs to retrieve
        user_id: Optional user ID to filter logs

    Returns:
        List of audit log entries
    """
    query = AuditLog.query

    if user_id:
        query = query.filter_by(user_id=user_id)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [log.to_dict() for log in logs]
