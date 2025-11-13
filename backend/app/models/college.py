"""
College and Course models
"""
from datetime import datetime
from . import db


class College(db.Model):
    """College model"""
    __tablename__ = 'colleges'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum('Government', 'Private', 'Aided'), nullable=False)
    university = db.Column(db.String(255), nullable=True)

    # Location
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=True)

    # Contact
    phone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(500), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    courses = db.relationship('Course', backref='college', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_courses=False):
        """Convert college to dictionary"""
        data = {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'type': self.type,
            'university': self.university,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_courses:
            data['courses'] = [course.to_dict() for course in self.courses.filter_by(is_active=True)]

        return data

    def __repr__(self):
        return f'<College {self.code} - {self.name}>'


class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=False, index=True)

    # Course Information
    code = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    degree = db.Column(db.String(50), nullable=False)  # B.E., B.Tech, etc.
    branch = db.Column(db.String(100), nullable=False)  # CSE, ECE, Mechanical, etc.
    duration_years = db.Column(db.Integer, nullable=False, default=4)

    # Seat Information
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)

    # Seat Breakdown by Category
    general_seats = db.Column(db.Integer, nullable=False, default=0)
    obc_seats = db.Column(db.Integer, nullable=False, default=0)
    sc_seats = db.Column(db.Integer, nullable=False, default=0)
    st_seats = db.Column(db.Integer, nullable=False, default=0)
    ews_seats = db.Column(db.Integer, nullable=False, default=0)

    # Fee Information
    tuition_fee = db.Column(db.Numeric(10, 2), nullable=False)
    other_fees = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # Eligibility
    min_rank = db.Column(db.Integer, nullable=True)
    max_rank = db.Column(db.Integer, nullable=True)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    choices = db.relationship('Choice', backref='course', lazy='dynamic')
    allotments = db.relationship('Allotment', backref='course', lazy='dynamic')

    # Unique constraint for college-course combination
    __table_args__ = (
        db.UniqueConstraint('college_id', 'code', name='uq_college_course'),
    )

    @property
    def total_fee(self):
        """Calculate total fee"""
        return float(self.tuition_fee + self.other_fees)

    def to_dict(self, include_college=False):
        """Convert course to dictionary"""
        data = {
            'id': self.id,
            'college_id': self.college_id,
            'code': self.code,
            'name': self.name,
            'degree': self.degree,
            'branch': self.branch,
            'duration_years': self.duration_years,
            'total_seats': self.total_seats,
            'available_seats': self.available_seats,
            'general_seats': self.general_seats,
            'obc_seats': self.obc_seats,
            'sc_seats': self.sc_seats,
            'st_seats': self.st_seats,
            'ews_seats': self.ews_seats,
            'tuition_fee': float(self.tuition_fee),
            'other_fees': float(self.other_fees),
            'total_fee': self.total_fee,
            'min_rank': self.min_rank,
            'max_rank': self.max_rank,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_college and self.college:
            data['college'] = self.college.to_dict()

        return data

    def __repr__(self):
        return f'<Course {self.code} - {self.name} at {self.college.name}>'
