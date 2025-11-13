"""
Document model for managing student documents
"""
from datetime import datetime
from enum import Enum
from . import db


class DocumentType(str, Enum):
    """Document type enumeration"""
    MARKS_CARD_10TH = 'marks_card_10th'
    MARKS_CARD_12TH = 'marks_card_12th'
    RANK_CARD = 'rank_card'
    DOMICILE_CERTIFICATE = 'domicile_certificate'
    CATEGORY_CERTIFICATE = 'category_certificate'
    PWD_CERTIFICATE = 'pwd_certificate'
    PHOTO = 'photo'
    SIGNATURE = 'signature'
    AADHAR_CARD = 'aadhar_card'
    OTHER = 'other'


class DocumentStatus(str, Enum):
    """Document verification status"""
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'


class Document(db.Model):
    """Document model"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)

    # Document Information
    document_type = db.Column(db.Enum(DocumentType), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_extension = db.Column(db.String(10), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)

    # Verification Information
    status = db.Column(db.Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    verifier = db.relationship('User', foreign_keys=[verified_by], backref='verified_documents')

    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'document_type': self.document_type.value,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_extension': self.file_extension,
            'status': self.status.value,
            'verified_by': self.verified_by,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'rejection_reason': self.rejection_reason,
            'uploaded_at': self.uploaded_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Document {self.document_type.value} - {self.status.value}>'
