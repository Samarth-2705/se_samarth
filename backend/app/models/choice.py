"""
Choice model for student college/course preferences
"""
from datetime import datetime
from . import db


class Choice(db.Model):
    """Choice model for student preferences"""
    __tablename__ = 'choices'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)

    # Preference order (1 = highest preference)
    preference_order = db.Column(db.Integer, nullable=False)

    # Status
    is_locked = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=True)

    # Unique constraint for student-course combination
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='uq_student_course_choice'),
        db.UniqueConstraint('student_id', 'preference_order', name='uq_student_preference_order'),
    )

    def to_dict(self, include_course=False, include_college=False):
        """Convert choice to dictionary"""
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'preference_order': self.preference_order,
            'is_locked': self.is_locked,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

        if include_course and self.course:
            data['course'] = self.course.to_dict(include_college=include_college)

        # Include college data directly for frontend convenience
        if include_college and self.course and self.course.college:
            data['college'] = self.course.college.to_dict()

        return data

    def __repr__(self):
        return f'<Choice Student:{self.student_id} Course:{self.course_id} Pref:{self.preference_order}>'
