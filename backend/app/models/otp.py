"""
OTP model for one-time password verification
"""
from datetime import datetime, timedelta
from enum import Enum
import secrets
from . import db


class OTPPurpose(str, Enum):
    """OTP purpose enumeration"""
    EMAIL_VERIFICATION = 'email_verification'
    MOBILE_VERIFICATION = 'mobile_verification'
    PASSWORD_RESET = 'password_reset'
    LOGIN_2FA = 'login_2fa'
    TRANSACTION = 'transaction'


class OTP(db.Model):
    """OTP model for verification"""
    __tablename__ = 'otps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    # OTP Details
    code = db.Column(db.String(10), nullable=False, index=True)
    purpose = db.Column(db.Enum(OTPPurpose), nullable=False)

    # Contact Information
    email = db.Column(db.String(255), nullable=True, index=True)
    mobile = db.Column(db.String(15), nullable=True, index=True)

    # Status
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    is_expired = db.Column(db.Boolean, default=False, nullable=False)

    # Validity
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

    # Verification Attempts
    verification_attempts = db.Column(db.Integer, default=0, nullable=False)
    max_attempts = db.Column(db.Integer, default=3, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='otps', foreign_keys=[user_id])

    @staticmethod
    def generate_code(length=6):
        """Generate a random OTP code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

    @classmethod
    def create_otp(cls, purpose, validity_minutes=5, email=None, mobile=None, user_id=None, length=6):
        """Create a new OTP"""
        code = cls.generate_code(length)
        expires_at = datetime.utcnow() + timedelta(minutes=validity_minutes)

        otp = cls(
            user_id=user_id,
            code=code,
            purpose=purpose,
            email=email,
            mobile=mobile,
            expires_at=expires_at
        )

        return otp

    def is_valid(self):
        """Check if OTP is valid"""
        if self.is_used:
            return False
        if self.is_expired:
            return False
        if datetime.utcnow() > self.expires_at:
            self.is_expired = True
            return False
        if self.verification_attempts >= self.max_attempts:
            return False
        return True

    def verify(self, code):
        """Verify OTP code"""
        self.verification_attempts += 1

        if not self.is_valid():
            return False

        if self.code == code:
            self.is_used = True
            self.used_at = datetime.utcnow()
            return True

        return False

    def to_dict(self):
        """Convert OTP to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'purpose': self.purpose.value,
            'email': self.email,
            'mobile': self.mobile,
            'is_used': self.is_used,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'is_expired': self.is_expired,
            'expires_at': self.expires_at.isoformat(),
            'verification_attempts': self.verification_attempts,
            'max_attempts': self.max_attempts,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<OTP {self.id} - {self.purpose.value} - {"Used" if self.is_used else "Valid" if self.is_valid() else "Invalid"}>'
