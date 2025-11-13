"""
Seat allotment routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Student, Allotment, AllotmentRound, UserRole, AuditLog
from app.services.seat_allotment_service import SeatAllotmentService

bp = Blueprint('allotment', __name__)


@bp.route('/my-allotment', methods=['GET'])
@jwt_required()
def get_my_allotment():
    """Get student's allotment details"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Get latest allotment
        allotment = Allotment.query.filter_by(student_id=student.id)\
            .order_by(Allotment.allotted_at.desc()).first()

        if not allotment:
            return jsonify({
                'allotment': None,
                'message': 'No seat allotted yet'
            }), 200

        return jsonify({
            'allotment': allotment.to_dict(include_student=False, include_course=True, include_college=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:allotment_id>/accept', methods=['POST'])
@jwt_required()
def accept_allotment(allotment_id):
    """Accept an allotted seat"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        allotment = Allotment.query.get(allotment_id)
        if not allotment:
            return jsonify({'error': 'Allotment not found'}), 404

        # Verify allotment belongs to student
        if allotment.student.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        freeze = data.get('freeze', True)  # True = freeze, False = upgrade

        # Accept seat
        success = SeatAllotmentService.accept_seat(allotment_id, freeze)

        if success:
            # Log action
            AuditLog.log_action(
                user_id=user.id,
                action='seat_accepted',
                entity_type='Allotment',
                entity_id=allotment.id,
                description=f'Seat {"frozen" if freeze else "accepted with upgrade"}'
            )
            db.session.commit()

            return jsonify({
                'message': 'Seat accepted successfully',
                'frozen': freeze
            }), 200
        else:
            return jsonify({'error': 'Failed to accept seat'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:allotment_id>/reject', methods=['POST'])
@jwt_required()
def reject_allotment(allotment_id):
    """Reject an allotted seat"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        allotment = Allotment.query.get(allotment_id)
        if not allotment:
            return jsonify({'error': 'Allotment not found'}), 404

        # Verify allotment belongs to student
        if allotment.student.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        reason = data.get('reason', 'No reason provided')

        # Reject seat
        success = SeatAllotmentService.reject_seat(allotment_id, reason)

        if success:
            # Log action
            AuditLog.log_action(
                user_id=user.id,
                action='seat_rejected',
                entity_type='Allotment',
                entity_id=allotment.id,
                description=f'Seat rejected: {reason}'
            )
            db.session.commit()

            return jsonify({'message': 'Seat rejected successfully'}), 200
        else:
            return jsonify({'error': 'Failed to reject seat'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/rounds', methods=['GET'])
@jwt_required()
def get_allotment_rounds():
    """Get all allotment rounds"""
    try:
        rounds = AllotmentRound.query.order_by(AllotmentRound.round_number).all()

        return jsonify({
            'rounds': [round.to_dict() for round in rounds]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/round/<int:round_id>', methods=['GET'])
@jwt_required()
def get_round_details(round_id):
    """Get details of a specific round"""
    try:
        allotment_round = AllotmentRound.query.get(round_id)
        if not allotment_round:
            return jsonify({'error': 'Round not found'}), 404

        return jsonify({
            'round': allotment_round.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_allotment_statistics():
    """Get allotment statistics (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        # Get statistics
        from sqlalchemy import func
        from app.models import AllotmentStatus

        total_allotments = Allotment.query.count()
        accepted_frozen = Allotment.query.filter_by(status=AllotmentStatus.ACCEPTED_FROZEN).count()
        accepted_upgrade = Allotment.query.filter_by(status=AllotmentStatus.ACCEPTED_UPGRADE).count()
        rejected = Allotment.query.filter_by(status=AllotmentStatus.REJECTED).count()
        pending = Allotment.query.filter_by(status=AllotmentStatus.ALLOTTED).count()

        # Round-wise statistics
        rounds = AllotmentRound.query.all()
        round_stats = []
        for round in rounds:
            round_stats.append({
                'round_number': round.round_number,
                'total_allotments': round.total_allotments,
                'accepted_count': round.accepted_count,
                'rejected_count': round.rejected_count,
                'is_completed': round.is_completed
            })

        return jsonify({
            'overall': {
                'total_allotments': total_allotments,
                'accepted_frozen': accepted_frozen,
                'accepted_upgrade': accepted_upgrade,
                'rejected': rejected,
                'pending': pending
            },
            'rounds': round_stats
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
