"""
SMS service for sending notifications via Twilio
"""
from flask import current_app
from twilio.rest import Client
from datetime import datetime
from app.models import db, Notification, NotificationType


class SMSService:
    """Service for sending SMS"""

    @staticmethod
    def get_client():
        """Get Twilio client"""
        try:
            account_sid = current_app.config['TWILIO_ACCOUNT_SID']
            auth_token = current_app.config['TWILIO_AUTH_TOKEN']

            if not account_sid or not auth_token:
                current_app.logger.warning("Twilio credentials not configured")
                return None

            return Client(account_sid, auth_token)
        except Exception as e:
            current_app.logger.error(f"Failed to initialize Twilio client: {str(e)}")
            return None

    @staticmethod
    def send_sms(to, message, user_id=None):
        """
        Send an SMS

        Args:
            to: Recipient mobile number (with country code)
            message: SMS message
            user_id: User ID for notification tracking

        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        try:
            client = SMSService.get_client()
            if not client:
                current_app.logger.error("Twilio client not available")
                return False

            from_number = current_app.config['TWILIO_PHONE_NUMBER']
            if not from_number:
                current_app.logger.error("Twilio phone number not configured")
                return False

            # Ensure phone number has country code
            if not to.startswith('+'):
                to = f"+91{to}"  # Default to India

            sms = client.messages.create(
                body=message,
                from_=from_number,
                to=to
            )

            # Log notification
            if user_id:
                notification = Notification(
                    user_id=user_id,
                    notification_type=NotificationType.SMS,
                    message=message,
                    mobile_to=to,
                    sms_id=sms.sid,
                    sent=True,
                    sent_at=datetime.utcnow(),
                    delivery_status=sms.status
                )
                db.session.add(notification)
                db.session.commit()

            return True

        except Exception as e:
            current_app.logger.error(f"Failed to send SMS: {str(e)}")

            # Log failed notification
            if user_id:
                notification = Notification(
                    user_id=user_id,
                    notification_type=NotificationType.SMS,
                    message=message,
                    mobile_to=to,
                    sent=False,
                    delivery_status='failed',
                    failure_reason=str(e)
                )
                db.session.add(notification)
                db.session.commit()

            return False

    @staticmethod
    def send_otp_sms(to, otp_code, user_id=None):
        """Send OTP via SMS"""
        message = f"Your OTP for Admission System is: {otp_code}. Valid for 5 minutes. Do not share with anyone."
        return SMSService.send_sms(to, message, user_id)

    @staticmethod
    def send_registration_confirmation_sms(to, name, user_id=None):
        """Send registration confirmation SMS"""
        message = f"Dear {name}, your registration is successful. Login to complete your application. - Admission System"
        return SMSService.send_sms(to, message, user_id)

    @staticmethod
    def send_document_verification_sms(to, name, document_type, status, user_id=None):
        """Send document verification status SMS"""
        status_text = "verified" if status == "verified" else "rejected"
        message = f"Dear {name}, your {document_type} has been {status_text}. Check your email for details. - Admission System"
        return SMSService.send_sms(to, message, user_id)

    @staticmethod
    def send_payment_confirmation_sms(to, name, amount, receipt_number, user_id=None):
        """Send payment confirmation SMS"""
        message = f"Dear {name}, payment of Rs.{amount} successful. Receipt: {receipt_number}. - Admission System"
        return SMSService.send_sms(to, message, user_id)

    @staticmethod
    def send_seat_allotment_sms(to, name, college, user_id=None):
        """Send seat allotment notification SMS"""
        message = f"Dear {name}, Congratulations! Seat allotted at {college}. Login to view details and accept. - Admission System"
        return SMSService.send_sms(to, message, user_id)
