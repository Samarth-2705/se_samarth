"""
Admin routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from app.models import (
    db, User, Student, Document, Payment, Allotment, AllotmentRound,
    College, Course, UserRole
)
from app.services.seat_allotment_service import SeatAllotmentService

bp = Blueprint('admin', __name__)


def require_admin():
    """Decorator to require admin role"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or user.role != UserRole.ADMIN:
        return None
    return user


@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        user = require_admin()
        if not user:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        # Get statistics
        total_students = Student.query.count()
        registrations_complete = Student.query.filter_by(registration_complete=True).count()
        documents_verified = Student.query.filter_by(documents_verified=True).count()
        payments_complete = Student.query.filter_by(payment_complete=True).count()
        choices_submitted = Student.query.filter_by(choices_submitted=True).count()
        seats_allotted = Student.query.filter_by(seat_allotted=True).count()
        admissions_confirmed = Student.query.filter_by(admission_confirmed=True).count()

        # Payment statistics
        total_revenue = db.session.query(func.sum(Payment.amount))\
            .filter_by(status='success').scalar() or 0

        # Document statistics
        documents_pending = Document.query.filter_by(status='pending').count()

        # College and course statistics
        total_colleges = College.query.filter_by(is_active=True).count()
        total_courses = Course.query.filter_by(is_active=True).count()
        total_seats = db.session.query(func.sum(Course.total_seats))\
            .filter_by(is_active=True).scalar() or 0
        available_seats = db.session.query(func.sum(Course.available_seats))\
            .filter_by(is_active=True).scalar() or 0

        return jsonify({
            'students': {
                'total': total_students,
                'registrations_complete': registrations_complete,
                'documents_verified': documents_verified,
                'payments_complete': payments_complete,
                'choices_submitted': choices_submitted,
                'seats_allotted': seats_allotted,
                'admissions_confirmed': admissions_confirmed
            },
            'financial': {
                'total_revenue': float(total_revenue)
            },
            'documents': {
                'pending_verification': documents_pending
            },
            'infrastructure': {
                'total_colleges': total_colleges,
                'total_courses': total_courses,
                'total_seats': total_seats,
                'available_seats': available_seats,
                'seats_filled': total_seats - available_seats
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/students', methods=['GET'])
@jwt_required()
def get_all_students():
    """Get all students with filtering"""
    try:
        user = require_admin()
        if not user:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')

        # Build query
        query = Student.query

        # Search filter
        if search:
            query = query.join(User).filter(
                or_(
                    Student.first_name.ilike(f'%{search}%'),
                    Student.last_name.ilike(f'%{search}%'),
                    Student.exam_roll_number.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )

        # Status filter
        if status == 'registered':
            query = query.filter_by(registration_complete=True)
        elif status == 'verified':
            query = query.filter_by(documents_verified=True)
        elif status == 'paid':
            query = query.filter_by(payment_complete=True)
        elif status == 'allotted':
            query = query.filter_by(seat_allotted=True)

        # Paginate
        pagination = query.order_by(Student.exam_rank).paginate(
            page=page, per_page=per_page, error_out=False
        )

        students = [student.to_dict(include_user=True) for student in pagination.items]

        return jsonify({
            'students': students,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/applications', methods=['GET'])
@jwt_required()
def generate_application_report():
    """Generate application report"""
    try:
        user = require_admin()
        if not user:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Student.query.join(User)

        if start_date:
            query = query.filter(User.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(User.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))

        students = query.all()

        report_data = []
        for student in students:
            report_data.append({
                'name': student.full_name,
                'email': student.user.email,
                'mobile': student.user.mobile,
                'exam_type': student.exam_type,
                'rank': student.exam_rank,
                'roll_number': student.exam_roll_number,
                'registration_date': student.user.created_at.isoformat(),
                'status': student.application_status,
                'payment_status': 'Paid' if student.payment_complete else 'Pending',
                'documents_verified': 'Yes' if student.documents_verified else 'No'
            })

        return jsonify({
            'report': report_data,
            'total_count': len(report_data),
            'generated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/allotment/trigger', methods=['POST'])
@jwt_required()
def trigger_allotment():
    """Trigger seat allotment for a round"""
    try:
        user = require_admin()
        if not user:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        data = request.get_json()

        if 'round_number' not in data:
            return jsonify({'error': 'Round number is required'}), 400

        round_number = data['round_number']

        # Check if round exists
        allotment_round = AllotmentRound.query.filter_by(round_number=round_number).first()

        if not allotment_round:
            # Create new round
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=7)
            acceptance_deadline = end_date + timedelta(days=3)

            allotment_round = SeatAllotmentService.create_allotment_round(
                round_number=round_number,
                start_date=start_date,
                end_date=end_date,
                acceptance_deadline=acceptance_deadline
            )

            if not allotment_round:
                return jsonify({'error': 'Failed to create allotment round'}), 500

        # Run allotment
        result = SeatAllotmentService.run_seat_allotment(allotment_round.id)

        if result.get('success'):
            return jsonify({
                'message': 'Seat allotment completed successfully',
                'result': result
            }), 200
        else:
            return jsonify({
                'error': 'Seat allotment failed',
                'details': result.get('error')
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/colleges', methods=['GET'])
@jwt_required()
def get_colleges():
    """Get all colleges"""
    try:
        colleges = College.query.filter_by(is_active=True).all()
        return jsonify({
            'colleges': [college.to_dict(include_courses=True) for college in colleges]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    """Get all courses"""
    try:
        courses = Course.query.filter_by(is_active=True).all()
        return jsonify({
            'courses': [course.to_dict(include_college=True) for course in courses]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
