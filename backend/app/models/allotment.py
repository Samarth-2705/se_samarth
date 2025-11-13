"""
Allotment model for seat allocation
"""
from datetime import datetime
from enum import Enum
from . import db


class AllotmentStatus(str, Enum):
    """Allotment status enumeration"""
    ALLOTTED = 'allotted'
    ACCEPTED_FROZEN = 'accepted_frozen'  # Student freezes the seat, no upgrade
    ACCEPTED_UPGRADE = 'accepted_upgrade'  # Student accepts but wants upgrade
    REJECTED = 'rejected'  # Student rejects the seat
    CANCELLED = 'cancelled'  # Admin cancelled
    UPGRADED = 'upgraded'  # Student got upgraded in next round


class AllotmentRound(db.Model):
    """Allotment round model"""
    __tablename__ = 'allotment_rounds'

    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, unique=True, nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    acceptance_deadline = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    # Statistics
    total_allotments = db.Column(db.Integer, default=0)
    accepted_count = db.Column(db.Integer, default=0)
    rejected_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    allotments = db.relationship('Allotment', backref='round', lazy='dynamic')

    def to_dict(self):
        """Convert round to dictionary"""
        return {
            'id': self.id,
            'round_number': self.round_number,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'acceptance_deadline': self.acceptance_deadline.isoformat(),
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'total_allotments': self.total_allotments,
            'accepted_count': self.accepted_count,
            'rejected_count': self.rejected_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<AllotmentRound {self.round_number}>'


class Allotment(db.Model):
    """Allotment model for seat allocation"""
    __tablename__ = 'allotments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    round_id = db.Column(db.Integer, db.ForeignKey('allotment_rounds.id'), nullable=False, index=True)

    # Allotment Details
    allotted_rank = db.Column(db.Integer, nullable=False)
    allotted_category = db.Column(db.Enum('General', 'OBC', 'SC', 'ST', 'EWS'), nullable=False)
    status = db.Column(db.Enum(AllotmentStatus), default=AllotmentStatus.ALLOTTED, nullable=False)

    # Acceptance Details
    acceptance_date = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Letter Generation
    allotment_letter_generated = db.Column(db.Boolean, default=False)
    allotment_letter_path = db.Column(db.String(500), nullable=True)

    # Timestamps
    allotted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Unique constraint: one allotment per student per round
    __table_args__ = (
        db.UniqueConstraint('student_id', 'round_id', name='uq_student_round_allotment'),
    )

    def to_dict(self, include_student=False, include_course=False, include_college=False):
        """Convert allotment to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'round_id': self.round_id,
            'allotted_rank': self.allotted_rank,
            'allotted_category': self.allotted_category,
            'status': self.status.value,
            'acceptance_date': self.acceptance_date.isoformat() if self.acceptance_date else None,
            'rejection_reason': self.rejection_reason,
            'allotment_letter_generated': self.allotment_letter_generated,
            'allotted_at': self.allotted_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_student and self.student:
            data['student'] = self.student.to_dict()

        if include_course and self.course:
            data['course'] = self.course.to_dict(include_college=include_college)

        # Include college data directly for frontend convenience
        if include_college and self.course and self.course.college:
            data['college'] = self.course.college.to_dict()

        if self.round:
            data['round'] = self.round.to_dict()

        return data

    def __repr__(self):
        return f'<Allotment Student:{self.student_id} Course:{self.course_id} Round:{self.round_id}>'
