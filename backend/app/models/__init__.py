"""
Database models for the Admission Automation System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# Import all models to make them available when importing from models
from .user import User, UserRole
from .student import Student
from .document import Document, DocumentType, DocumentStatus
from .college import College, Course
from .choice import Choice
from .allotment import Allotment, AllotmentStatus, AllotmentRound
from .payment import Payment, PaymentStatus, PaymentType
from .notification import Notification, NotificationType
from .otp import OTP, OTPPurpose
from .audit_log import AuditLog

__all__ = [
    'db',
    'bcrypt',
    'User',
    'UserRole',
    'Student',
    'Document',
    'DocumentType',
    'DocumentStatus',
    'College',
    'Course',
    'Choice',
    'Allotment',
    'AllotmentStatus',
    'AllotmentRound',
    'Payment',
    'PaymentStatus',
    'PaymentType',
    'Notification',
    'NotificationType',
    'OTP',
    'OTPPurpose',
    'AuditLog'
]
