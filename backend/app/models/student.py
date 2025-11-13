"""
Student model for student profile and academic information
"""
from datetime import datetime
from . import db


class Student(db.Model):
    """Student profile model"""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)

    # Contact Information
    address_line1 = db.Column(db.String(255), nullable=True)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)

    # Guardian Information
    guardian_name = db.Column(db.String(200), nullable=True)
    guardian_mobile = db.Column(db.String(15), nullable=True)
    guardian_email = db.Column(db.String(255), nullable=True)

    # Academic Information
    exam_type = db.Column(db.Enum('KCET', 'COMEDK', 'Other'), nullable=False)
    exam_rank = db.Column(db.Integer, nullable=False, index=True)
    exam_roll_number = db.Column(db.String(50), nullable=False, unique=True, index=True)

    # Category Information
    category = db.Column(db.Enum('General', 'OBC', 'SC', 'ST', 'EWS'), nullable=False)
    is_pwd = db.Column(db.Boolean, default=False)  # Person with Disability
    domicile_state = db.Column(db.String(100), nullable=False)

    # Application Status
    registration_complete = db.Column(db.Boolean, default=False)
    documents_verified = db.Column(db.Boolean, default=False)
    payment_complete = db.Column(db.Boolean, default=False)
    choices_submitted = db.Column(db.Boolean, default=False)
    seat_allotted = db.Column(db.Boolean, default=False)
    admission_confirmed = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    documents = db.relationship('Document', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    choices = db.relationship('Choice', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    allotments = db.relationship('Allotment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def full_name(self):
        """Get student's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def application_status(self):
        """Get current application status"""
        if self.admission_confirmed:
            return 'Admission Confirmed'
        elif self.seat_allotted:
            return 'Seat Allotted'
        elif self.choices_submitted:
            return 'Choices Submitted'
        elif self.payment_complete:
            return 'Payment Complete'
        elif self.documents_verified:
            return 'Documents Verified'
        elif self.registration_complete:
            return 'Registration Complete'
        else:
            return 'Registration Pending'

    def to_dict(self, include_user=False):
        """Convert student to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'guardian_name': self.guardian_name,
            'guardian_mobile': self.guardian_mobile,
            'guardian_email': self.guardian_email,
            'exam_type': self.exam_type,
            'exam_rank': self.exam_rank,
            'exam_roll_number': self.exam_roll_number,
            'category': self.category,
            'is_pwd': self.is_pwd,
            'domicile_state': self.domicile_state,
            'application_status': self.application_status,
            'registration_complete': self.registration_complete,
            'documents_verified': self.documents_verified,
            'payment_complete': self.payment_complete,
            'choices_submitted': self.choices_submitted,
            'seat_allotted': self.seat_allotted,
            'admission_confirmed': self.admission_confirmed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_user and self.user:
            data['user'] = self.user.to_dict()

        return data

    def __repr__(self):
        return f'<Student {self.full_name} (Rank: {self.exam_rank})>'
