"""
Student routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db, User, Student, UserRole, AuditLog
from app.utils.validators import validate_mobile, validate_pincode

bp = Blueprint('student', __name__)


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get student profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        if not user.student:
            return jsonify({'error': 'Student profile not found'}), 404

        return jsonify(user.student.to_dict(include_user=True)), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update student profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        data = request.get_json()

        # Update allowed fields
        updateable_fields = [
            'address_line1', 'address_line2', 'city', 'state', 'pincode',
            'guardian_name', 'guardian_mobile', 'guardian_email'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(student, field, data[field])

        # Validate pincode if provided
        if 'pincode' in data and data['pincode']:
            if not validate_pincode(data['pincode']):
                return jsonify({'error': 'Invalid pincode'}), 400

        # Validate guardian mobile if provided
        if 'guardian_mobile' in data and data['guardian_mobile']:
            if not validate_mobile(data['guardian_mobile']):
                return jsonify({'error': 'Invalid guardian mobile number'}), 400

        db.session.commit()

        # Log action
        AuditLog.log_action(
            user_id=user.id,
            action='profile_updated',
            entity_type='Student',
            entity_id=student.id,
            description='Student profile updated'
        )
        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/complete-registration', methods=['POST'])
@jwt_required()
def complete_registration():
    """Mark registration as complete"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Check if all required fields are filled
        required_fields = [
            student.address_line1, student.city, student.state,
            student.pincode, student.guardian_name, student.guardian_mobile
        ]

        if not all(required_fields):
            return jsonify({'error': 'Please fill all required fields'}), 400

        student.registration_complete = True
        db.session.commit()

        return jsonify({
            'message': 'Registration completed successfully',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get student dashboard data"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Get student statistics
        documents_count = student.documents.count()
        documents_verified = student.documents.filter_by(status='verified').count()
        choices_count = student.choices.count()
        payments_count = student.payments.filter_by(status='success').count()
        allotments = student.allotments.all()

        return jsonify({
            'student': student.to_dict(),
            'statistics': {
                'documents_uploaded': documents_count,
                'documents_verified': documents_verified,
                'choices_filled': choices_count,
                'payments_made': payments_count,
                'allotments': len(allotments)
            },
            'status': {
                'registration_complete': student.registration_complete,
                'documents_verified': student.documents_verified,
                'payment_complete': student.payment_complete,
                'choices_submitted': student.choices_submitted,
                'seat_allotted': student.seat_allotted,
                'admission_confirmed': student.admission_confirmed
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
