from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'pracownik', 'manager', 'admin'
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    token_version = db.Column(db.Integer, default=0)  # For JWT invalidation on password change

    # Relationships
    supervisor = db.relationship('User', remote_side=[id], backref='subordinates')
    requests_as_employee = db.relationship('Request', foreign_keys='Request.employee_id', backref='employee', cascade='all, delete-orphan')
    requests_as_manager = db.relationship('Request', foreign_keys='Request.manager_id', backref='manager')
    audit_logs = db.relationship('AuditLog', backref='user', cascade='all, delete-orphan')

    def to_dict(self, include_supervisor=True):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

        if include_supervisor and self.supervisor:
            data['supervisor'] = {
                'id': self.supervisor.id,
                'name': f"{self.supervisor.first_name} {self.supervisor.last_name}"
            }
        elif self.supervisor_id:
            data['supervisor_id'] = self.supervisor_id

        return data

    def __repr__(self):
        return f'<User {self.email}>'


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_out = db.Column(db.Time, nullable=False)
    time_return = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='oczekujący')  # 'oczekujący', 'zaakceptowany', 'odrzucony', 'anulowany'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    decision_date = db.Column(db.DateTime, nullable=True)
    manager_comment = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """Convert request to dictionary"""
        return {
            'id': self.id,
            'employee': {
                'id': self.employee.id,
                'name': f"{self.employee.first_name} {self.employee.last_name}",
                'email': self.employee.email
            },
            'manager': {
                'id': self.manager.id,
                'name': f"{self.manager.first_name} {self.manager.last_name}",
                'email': self.manager.email
            },
            'date': self.date.isoformat() if self.date else None,
            'time_out': self.time_out.strftime('%H:%M') if self.time_out else None,
            'time_return': self.time_return.strftime('%H:%M') if self.time_return else None,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'decision_date': self.decision_date.isoformat() if self.decision_date else None,
            'manager_comment': self.manager_comment
        }

    def __repr__(self):
        return f'<Request {self.id} - {self.status}>'


class SmtpConfig(db.Model):
    __tablename__ = 'smtp_config'

    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String(255), nullable=True)
    port = db.Column(db.Integer, default=587)
    use_ssl = db.Column(db.Boolean, default=True)
    login = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    email_from = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, mask_password=True):
        """Convert SMTP config to dictionary"""
        return {
            'id': self.id,
            'server': self.server,
            'port': self.port,
            'use_ssl': self.use_ssl,
            'login': self.login,
            'password': '***' if mask_password and self.password else self.password,
            'email_from': self.email_from,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<SmtpConfig {self.server}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': f"{self.user.first_name} {self.user.last_name}" if self.user else 'System',
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    def __repr__(self):
        return f'<AuditLog {self.action}>'
