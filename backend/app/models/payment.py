"""
Payment model for fee processing
"""
from datetime import datetime
from enum import Enum
from . import db


class PaymentType(str, Enum):
    """Payment type enumeration"""
    APPLICATION_FEE = 'application_fee'
    COUNSELLING_FEE = 'counselling_fee'
    ADMISSION_FEE = 'admission_fee'
    TUITION_FEE = 'tuition_fee'
    REFUND = 'refund'


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    INITIATED = 'initiated'
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    REFUND_PENDING = 'refund_pending'


class Payment(db.Model):
    """Payment model"""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)

    # Payment Details
    payment_type = db.Column(db.Enum(PaymentType), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='INR', nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.INITIATED, nullable=False)

    # Gateway Details
    gateway_name = db.Column(db.String(50), default='razorpay', nullable=False)
    gateway_order_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    gateway_payment_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    gateway_signature = db.Column(db.String(255), nullable=True)

    # Transaction Details
    payment_method = db.Column(db.String(50), nullable=True)  # card, upi, netbanking, wallet
    transaction_id = db.Column(db.String(255), unique=True, nullable=True, index=True)

    # Receipt Details
    receipt_number = db.Column(db.String(100), unique=True, nullable=True, index=True)
    receipt_path = db.Column(db.String(500), nullable=True)
    receipt_generated = db.Column(db.Boolean, default=False)

    # Refund Details
    refund_requested = db.Column(db.Boolean, default=False)
    refund_request_date = db.Column(db.DateTime, nullable=True)
    refund_approved = db.Column(db.Boolean, default=False)
    refund_approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    refund_approved_date = db.Column(db.DateTime, nullable=True)
    refund_amount = db.Column(db.Numeric(10, 2), nullable=True)
    refund_id = db.Column(db.String(255), nullable=True)
    refund_reason = db.Column(db.Text, nullable=True)

    # Failure Details
    failure_reason = db.Column(db.Text, nullable=True)
    error_code = db.Column(db.String(50), nullable=True)

    # Timestamps
    initiated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    refund_approver = db.relationship('User', foreign_keys=[refund_approved_by], backref='approved_refunds')

    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'payment_type': self.payment_type.value,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status.value,
            'gateway_name': self.gateway_name,
            'gateway_order_id': self.gateway_order_id,
            'gateway_payment_id': self.gateway_payment_id,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'receipt_number': self.receipt_number,
            'receipt_generated': self.receipt_generated,
            'refund_requested': self.refund_requested,
            'refund_request_date': self.refund_request_date.isoformat() if self.refund_request_date else None,
            'refund_approved': self.refund_approved,
            'refund_approved_date': self.refund_approved_date.isoformat() if self.refund_approved_date else None,
            'refund_amount': float(self.refund_amount) if self.refund_amount else None,
            'refund_reason': self.refund_reason,
            'failure_reason': self.failure_reason,
            'error_code': self.error_code,
            'initiated_at': self.initiated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Payment {self.id} - {self.payment_type.value} - {self.status.value}>'
