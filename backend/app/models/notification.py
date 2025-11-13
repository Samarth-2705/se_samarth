"""
Notification model for email and SMS notifications
"""
from datetime import datetime
from enum import Enum
from . import db


class NotificationType(str, Enum):
    """Notification type enumeration"""
    EMAIL = 'email'
    SMS = 'sms'
    BOTH = 'both'


class Notification(db.Model):
    """Notification model"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Notification Details
    notification_type = db.Column(db.Enum(NotificationType), nullable=False)
    subject = db.Column(db.String(255), nullable=True)  # For email
    message = db.Column(db.Text, nullable=False)

    # Delivery Status
    sent = db.Column(db.Boolean, default=False, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    delivery_status = db.Column(db.String(50), nullable=True)
    failure_reason = db.Column(db.Text, nullable=True)

    # Email Specific
    email_to = db.Column(db.String(255), nullable=True)
    email_from = db.Column(db.String(255), nullable=True)

    # SMS Specific
    mobile_to = db.Column(db.String(15), nullable=True)
    sms_id = db.Column(db.String(255), nullable=True)

    # Priority
    priority = db.Column(db.Enum('high', 'medium', 'low'), default='medium', nullable=False)

    # Retries
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    max_retries = db.Column(db.Integer, default=3, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type.value,
            'subject': self.subject,
            'message': self.message,
            'sent': self.sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivery_status': self.delivery_status,
            'failure_reason': self.failure_reason,
            'email_to': self.email_to,
            'mobile_to': self.mobile_to,
            'priority': self.priority,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Notification {self.id} - {self.notification_type.value} - {"Sent" if self.sent else "Pending"}>'
