"""
Payment service for Razorpay integration
"""
import razorpay
from flask import current_app
from datetime import datetime
from app.models import db, Payment, PaymentStatus, PaymentType
from app.services.email_service import EmailService
from app.services.sms_service import SMSService


class PaymentService:
    """Service for handling payments via Razorpay"""

    @staticmethod
    def get_client():
        """Get Razorpay client"""
        try:
            key_id = current_app.config['RAZORPAY_KEY_ID']
            key_secret = current_app.config['RAZORPAY_KEY_SECRET']

            if not key_id or not key_secret:
                current_app.logger.warning("Razorpay credentials not configured")
                return None

            return razorpay.Client(auth=(key_id, key_secret))
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Razorpay client: {str(e)}")
            return None

    @staticmethod
    def create_order(student_id, amount, payment_type, currency='INR'):
        """
        Create a payment order

        Args:
            student_id: Student ID
            amount: Amount in rupees
            payment_type: Type of payment (application_fee, admission_fee, etc.)
            currency: Currency code (default INR)

        Returns:
            dict: Payment order details or None
        """
        try:
            client = PaymentService.get_client()

            # Test mode if no Razorpay client
            if not client:
                current_app.logger.info("Running in test payment mode")
                # Create test order
                test_order_id = f"test_order_{int(datetime.utcnow().timestamp())}"

                # Create payment record
                payment = Payment(
                    student_id=student_id,
                    payment_type=payment_type,
                    amount=amount,
                    currency=currency,
                    status=PaymentStatus.INITIATED,
                    gateway_name='test_mode',
                    gateway_order_id=test_order_id,
                    order_id=test_order_id
                )
                db.session.add(payment)
                db.session.commit()

                return {
                    'id': payment.id,
                    'payment_id': payment.id,
                    'order_id': test_order_id,
                    'amount': amount,
                    'currency': currency,
                    'test_mode': True
                }

            # Production mode with Razorpay
            # Convert amount to paise (Razorpay uses paise)
            amount_paise = int(float(amount) * 100)

            # Create order
            order = client.order.create({
                'amount': amount_paise,
                'currency': currency,
                'payment_capture': 1  # Auto capture
            })

            # Create payment record
            payment = Payment(
                student_id=student_id,
                payment_type=payment_type,
                amount=amount,
                currency=currency,
                status=PaymentStatus.INITIATED,
                gateway_name='razorpay',
                gateway_order_id=order['id'],
                order_id=order['id']
            )
            db.session.add(payment)
            db.session.commit()

            return {
                'id': payment.id,
                'payment_id': payment.id,
                'order_id': order['id'],
                'amount': amount,
                'currency': currency,
                'key_id': current_app.config['RAZORPAY_KEY_ID']
            }

        except Exception as e:
            current_app.logger.error(f"Failed to create payment order: {str(e)}")
            return None

    @staticmethod
    def verify_payment(payment_id, razorpay_payment_id, razorpay_signature):
        """
        Verify payment signature

        Args:
            payment_id: Payment ID from database
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature from Razorpay

        Returns:
            bool: True if verification successful
        """
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return False

            client = PaymentService.get_client()

            # Test mode if no Razorpay client
            if not client or payment.gateway_name == 'test_mode':
                current_app.logger.info("Verifying test payment")

                # Update payment record for test mode
                payment.gateway_payment_id = razorpay_payment_id
                payment.gateway_signature = razorpay_signature
                payment.status = PaymentStatus.SUCCESS
                payment.payment_method = 'test'
                payment.transaction_id = razorpay_payment_id
                payment.completed_at = datetime.utcnow()

                # Generate receipt number
                payment.receipt_number = f"REC{payment.id:08d}"
                payment.receipt_generated = True

                db.session.commit()

                # Update student's payment status
                student = payment.student
                if student:
                    if payment.payment_type == PaymentType.APPLICATION_FEE:
                        student.payment_complete = True
                        db.session.commit()

                    # Send confirmation notifications (will only work if email/SMS configured)
                    if student.user:
                        try:
                            EmailService.send_payment_confirmation(
                                student.user.email,
                                student.full_name,
                                payment.amount,
                                payment.receipt_number,
                                student.user_id
                            )
                        except:
                            pass  # Ignore email failures in test mode

                        try:
                            SMSService.send_payment_confirmation_sms(
                                student.user.mobile,
                                student.full_name,
                                payment.amount,
                                payment.receipt_number,
                                student.user_id
                            )
                        except:
                            pass  # Ignore SMS failures in test mode

                return True

            # Production mode with Razorpay
            # Verify signature
            params_dict = {
                'razorpay_order_id': payment.gateway_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            client.utility.verify_payment_signature(params_dict)

            # Fetch payment details from Razorpay
            payment_details = client.payment.fetch(razorpay_payment_id)

            # Update payment record
            payment.gateway_payment_id = razorpay_payment_id
            payment.gateway_signature = razorpay_signature
            payment.status = PaymentStatus.SUCCESS
            payment.payment_method = payment_details.get('method')
            payment.transaction_id = payment_details.get('id')
            payment.completed_at = datetime.utcnow()

            # Generate receipt number
            payment.receipt_number = f"REC{payment.id:08d}"
            payment.receipt_generated = True

            db.session.commit()

            # Update student's payment status
            student = payment.student
            if student:
                if payment.payment_type == PaymentType.APPLICATION_FEE:
                    student.payment_complete = True
                    db.session.commit()

                # Send confirmation notifications
                if student.user:
                    EmailService.send_payment_confirmation(
                        student.user.email,
                        student.full_name,
                        payment.amount,
                        payment.receipt_number,
                        student.user_id
                    )
                    SMSService.send_payment_confirmation_sms(
                        student.user.mobile,
                        student.full_name,
                        payment.amount,
                        payment.receipt_number,
                        student.user_id
                    )

            return True

        except razorpay.errors.SignatureVerificationError:
            current_app.logger.error("Payment signature verification failed")
            if payment:
                payment.status = PaymentStatus.FAILED
                payment.failure_reason = "Signature verification failed"
                db.session.commit()
            return False

        except Exception as e:
            current_app.logger.error(f"Payment verification failed: {str(e)}")
            if payment:
                payment.status = PaymentStatus.FAILED
                payment.failure_reason = str(e)
                db.session.commit()
            return False

    @staticmethod
    def request_refund(payment_id, reason):
        """
        Request a refund for a payment

        Args:
            payment_id: Payment ID
            reason: Reason for refund

        Returns:
            bool: True if request successful
        """
        try:
            payment = Payment.query.get(payment_id)
            if not payment or payment.status != PaymentStatus.SUCCESS:
                return False

            payment.refund_requested = True
            payment.refund_request_date = datetime.utcnow()
            payment.refund_reason = reason
            payment.status = PaymentStatus.REFUND_PENDING

            db.session.commit()
            return True

        except Exception as e:
            current_app.logger.error(f"Refund request failed: {str(e)}")
            return False

    @staticmethod
    def process_refund(payment_id, admin_user_id):
        """
        Process a refund (admin action)

        Args:
            payment_id: Payment ID
            admin_user_id: Admin user ID

        Returns:
            bool: True if refund processed successfully
        """
        try:
            payment = Payment.query.get(payment_id)
            if not payment or not payment.refund_requested:
                return False

            client = PaymentService.get_client()
            if not client:
                return False

            # Process refund via Razorpay
            refund = client.payment.refund(
                payment.gateway_payment_id,
                {
                    'amount': int(float(payment.amount) * 100),  # Convert to paise
                    'speed': 'normal'
                }
            )

            # Update payment record
            payment.refund_approved = True
            payment.refund_approved_by = admin_user_id
            payment.refund_approved_date = datetime.utcnow()
            payment.refund_amount = payment.amount
            payment.refund_id = refund['id']
            payment.status = PaymentStatus.REFUNDED

            db.session.commit()
            return True

        except Exception as e:
            current_app.logger.error(f"Refund processing failed: {str(e)}")
            return False
