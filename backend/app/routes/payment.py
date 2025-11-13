"""
Payment routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Payment, PaymentType, UserRole
from app.services.payment_service import PaymentService

bp = Blueprint('payment', __name__)


@bp.route('/create-order', methods=['POST'])
@jwt_required()
def create_payment_order():
    """Create a payment order"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        data = request.get_json()

        if 'amount' not in data or 'payment_type' not in data:
            return jsonify({'error': 'Amount and payment type are required'}), 400

        try:
            payment_type = PaymentType(data['payment_type'])
        except ValueError:
            return jsonify({'error': 'Invalid payment type'}), 400

        # Create order
        order = PaymentService.create_order(
            student_id=student.id,
            amount=data['amount'],
            payment_type=payment_type
        )

        if not order:
            return jsonify({'error': 'Failed to create payment order'}), 500

        return jsonify({
            'message': 'Payment order created successfully',
            'order': order
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """Verify payment after successful transaction"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()

        required_fields = ['payment_id', 'razorpay_payment_id', 'razorpay_signature']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Verify payment
        success = PaymentService.verify_payment(
            payment_id=data['payment_id'],
            razorpay_payment_id=data['razorpay_payment_id'],
            razorpay_signature=data['razorpay_signature']
        )

        if success:
            return jsonify({'message': 'Payment verified successfully'}), 200
        else:
            return jsonify({'error': 'Payment verification failed'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get payment history"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        payments = Payment.query.filter_by(student_id=student.id)\
            .order_by(Payment.initiated_at.desc()).all()

        return jsonify({
            'payments': [payment.to_dict() for payment in payments]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:payment_id>/request-refund', methods=['POST'])
@jwt_required()
def request_refund(payment_id):
    """Request a refund"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Check if payment belongs to the student
        if payment.student.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        reason = data.get('reason', 'No reason provided')

        # Request refund
        success = PaymentService.request_refund(payment_id, reason)

        if success:
            return jsonify({'message': 'Refund requested successfully'}), 200
        else:
            return jsonify({'error': 'Failed to request refund'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:payment_id>/process-refund', methods=['POST'])
@jwt_required()
def process_refund(payment_id):
    """Process a refund (admin only)"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        success = PaymentService.process_refund(payment_id, user.id)

        if success:
            return jsonify({'message': 'Refund processed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to process refund'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
