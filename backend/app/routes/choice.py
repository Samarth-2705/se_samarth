"""
Choice filling routes
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db, User, Student, Choice, Course, College, UserRole, AuditLog
from sqlalchemy import and_

bp = Blueprint('choice', __name__)


@bp.route('/eligible-colleges', methods=['GET'])
@jwt_required()
def get_eligible_colleges():
    """Get list of eligible colleges based on student rank"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Get courses within rank range and with available seats
        courses = Course.query.join(College).filter(
            and_(
                Course.is_active == True,
                College.is_active == True,
                Course.available_seats > 0,
                Course.min_rank <= student.exam_rank,
                Course.max_rank >= student.exam_rank
            )
        ).all()

        # Group by college
        colleges_data = {}
        for course in courses:
            college = course.college
            if college.id not in colleges_data:
                colleges_data[college.id] = {
                    'college': college.to_dict(),
                    'courses': []
                }
            colleges_data[college.id]['courses'].append(course.to_dict())

        return jsonify({
            'eligible_colleges': list(colleges_data.values()),
            'total_colleges': len(colleges_data),
            'total_courses': len(courses)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/add', methods=['POST'])
@jwt_required()
def add_choice():
    """Add a college/course to choice list"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Check if choices are locked
        if student.choices_submitted:
            return jsonify({'error': 'Choices are already submitted and locked'}), 400

        data = request.get_json()

        if 'course_id' not in data:
            return jsonify({'error': 'Course ID is required'}), 400

        course = Course.query.get(data['course_id'])
        if not course or not course.is_active:
            return jsonify({'error': 'Invalid course'}), 404

        # Check max choices limit
        max_choices = current_app.config['MAX_CHOICES']
        existing_choices_count = Choice.query.filter_by(student_id=student.id).count()

        if existing_choices_count >= max_choices:
            return jsonify({'error': f'Maximum {max_choices} choices allowed'}), 400

        # Check if choice already exists
        existing_choice = Choice.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()

        if existing_choice:
            return jsonify({'error': 'Course already added to choices'}), 400

        # Add choice with next preference order
        preference_order = existing_choices_count + 1

        choice = Choice(
            student_id=student.id,
            course_id=course.id,
            preference_order=preference_order
        )

        db.session.add(choice)
        db.session.commit()

        return jsonify({
            'message': 'Choice added successfully',
            'choice': choice.to_dict(include_course=True, include_college=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/list', methods=['GET'])
@jwt_required()
def list_choices():
    """Get student's choices"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        choices = Choice.query.filter_by(student_id=student.id)\
            .order_by(Choice.preference_order).all()

        return jsonify({
            'choices': [choice.to_dict(include_course=True, include_college=True) for choice in choices],
            'total_choices': len(choices),
            'max_choices': current_app.config['MAX_CHOICES'],
            'submitted': student.choices_submitted
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:choice_id>/remove', methods=['DELETE'])
@jwt_required()
def remove_choice(choice_id):
    """Remove a choice"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Check if choices are locked
        if student.choices_submitted:
            return jsonify({'error': 'Choices are already submitted and locked'}), 400

        choice = Choice.query.get(choice_id)
        if not choice or choice.student_id != student.id:
            return jsonify({'error': 'Choice not found'}), 404

        preference_order = choice.preference_order

        db.session.delete(choice)

        # Reorder remaining choices
        remaining_choices = Choice.query.filter_by(student_id=student.id)\
            .filter(Choice.preference_order > preference_order)\
            .order_by(Choice.preference_order).all()

        for c in remaining_choices:
            c.preference_order -= 1

        db.session.commit()

        return jsonify({'message': 'Choice removed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/reorder', methods=['PUT'])
@jwt_required()
def reorder_choices():
    """Reorder choices"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Check if choices are locked
        if student.choices_submitted:
            return jsonify({'error': 'Choices are already submitted and locked'}), 400

        data = request.get_json()

        if 'choices' not in data:
            return jsonify({'error': 'Choices array is required'}), 400

        # Update preference orders
        for item in data['choices']:
            choice = Choice.query.get(item['choice_id'])
            if choice and choice.student_id == student.id:
                choice.preference_order = item['preference_order']

        db.session.commit()

        return jsonify({'message': 'Choices reordered successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_choices():
    """Submit and lock choices"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Check if already submitted
        if student.choices_submitted:
            return jsonify({'error': 'Choices are already submitted'}), 400

        # Check minimum choices
        min_choices = current_app.config['MIN_CHOICES']
        choices_count = Choice.query.filter_by(student_id=student.id).count()

        if choices_count < min_choices:
            return jsonify({'error': f'Minimum {min_choices} choice(s) required'}), 400

        # Lock all choices
        choices = Choice.query.filter_by(student_id=student.id).all()
        for choice in choices:
            choice.is_locked = True
            choice.submitted_at = datetime.utcnow()

        # Update student status
        student.choices_submitted = True

        db.session.commit()

        # Log action
        AuditLog.log_action(
            user_id=user.id,
            action='choices_submitted',
            entity_type='Student',
            entity_id=student.id,
            description=f'Submitted {choices_count} choices'
        )
        db.session.commit()

        return jsonify({
            'message': 'Choices submitted successfully',
            'choices_count': choices_count
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
