"""
Audit log model for tracking system activities
"""
from datetime import datetime
from . import db


class AuditLog(db.Model):
    """Audit log model"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    # Action Details
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=True, index=True)  # User, Student, Document, etc.
    entity_id = db.Column(db.Integer, nullable=True, index=True)

    # Request Details
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.String(500), nullable=True)
    request_method = db.Column(db.String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = db.Column(db.String(500), nullable=True)

    # Details
    description = db.Column(db.Text, nullable=True)
    old_values = db.Column(db.JSON, nullable=True)  # Store old values for updates
    new_values = db.Column(db.JSON, nullable=True)  # Store new values for updates

    # Status
    status = db.Column(db.String(20), nullable=True)  # success, failure, error
    error_message = db.Column(db.Text, nullable=True)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_method': self.request_method,
            'request_path': self.request_path,
            'description': self.description,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def log_action(cls, user_id, action, entity_type=None, entity_id=None,
                   description=None, old_values=None, new_values=None,
                   ip_address=None, user_agent=None, request_method=None,
                   request_path=None, status='success', error_message=None):
        """Create an audit log entry"""
        log = cls(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            status=status,
            error_message=error_message
        )
        db.session.add(log)
        return log

    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action} by User:{self.user_id}>'
