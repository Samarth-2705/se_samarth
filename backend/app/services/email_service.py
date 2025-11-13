"""
Email service for sending notifications
"""
from flask_mail import Mail, Message
from flask import current_app
from datetime import datetime
from app.models import db, Notification, NotificationType

mail = Mail()


class EmailService:
    """Service for sending emails"""

    @staticmethod
    def send_email(to, subject, body, html=None, user_id=None):
        """
        Send an email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html: HTML body (optional)
            user_id: User ID for notification tracking

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=html,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )

            mail.send(msg)

            # Log notification
            if user_id:
                notification = Notification(
                    user_id=user_id,
                    notification_type=NotificationType.EMAIL,
                    subject=subject,
                    message=body,
                    email_to=to,
                    email_from=current_app.config['MAIL_DEFAULT_SENDER'],
                    sent=True,
                    sent_at=datetime.utcnow(),
                    delivery_status='success'
                )
                db.session.add(notification)
                db.session.commit()

            return True

        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

            # Log failed notification
            if user_id:
                notification = Notification(
                    user_id=user_id,
                    notification_type=NotificationType.EMAIL,
                    subject=subject,
                    message=body,
                    email_to=to,
                    email_from=current_app.config['MAIL_DEFAULT_SENDER'],
                    sent=False,
                    delivery_status='failed',
                    failure_reason=str(e)
                )
                db.session.add(notification)
                db.session.commit()

            return False

    @staticmethod
    def send_otp_email(to, otp_code, purpose, user_id=None):
        """Send OTP via email"""
        subject = f"Your OTP for {purpose}"
        body = f"""
        Dear User,

        Your One-Time Password (OTP) for {purpose} is: {otp_code}

        This OTP is valid for 5 minutes. Please do not share this OTP with anyone.

        If you did not request this OTP, please ignore this email.

        Regards,
        Admission Automation System
        """

        html = f"""
        <html>
            <body>
                <h2>Your OTP for {purpose}</h2>
                <p>Dear User,</p>
                <p>Your One-Time Password (OTP) is:</p>
                <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{otp_code}</h1>
                <p>This OTP is valid for <strong>5 minutes</strong>. Please do not share this OTP with anyone.</p>
                <p>If you did not request this OTP, please ignore this email.</p>
                <br>
                <p>Regards,<br>Admission Automation System</p>
            </body>
        </html>
        """

        return EmailService.send_email(to, subject, body, html, user_id)

    @staticmethod
    def send_registration_confirmation(to, name, user_id=None):
        """Send registration confirmation email"""
        subject = "Registration Successful - Admission Automation System"
        body = f"""
        Dear {name},

        Congratulations! Your registration has been completed successfully.

        You can now log in to your account and complete your application process.

        Next steps:
        1. Complete your profile
        2. Upload required documents
        3. Pay application fee
        4. Fill your college preferences

        For any assistance, please contact our support team.

        Regards,
        Admission Automation System
        """

        html = f"""
        <html>
            <body>
                <h2>Registration Successful!</h2>
                <p>Dear {name},</p>
                <p>Congratulations! Your registration has been completed successfully.</p>
                <p>You can now log in to your account and complete your application process.</p>
                <h3>Next steps:</h3>
                <ol>
                    <li>Complete your profile</li>
                    <li>Upload required documents</li>
                    <li>Pay application fee</li>
                    <li>Fill your college preferences</li>
                </ol>
                <p>For any assistance, please contact our support team.</p>
                <br>
                <p>Regards,<br>Admission Automation System</p>
            </body>
        </html>
        """

        return EmailService.send_email(to, subject, body, html, user_id)

    @staticmethod
    def send_document_verification_notification(to, name, document_type, status, reason=None, user_id=None):
        """Send document verification status notification"""
        status_text = "verified" if status == "verified" else "rejected"
        subject = f"Document {status_text.capitalize()} - {document_type}"

        if status == "verified":
            body = f"""
            Dear {name},

            Your {document_type} has been verified successfully.

            You can proceed with the next steps in your application process.

            Regards,
            Admission Automation System
            """
        else:
            body = f"""
            Dear {name},

            Your {document_type} has been rejected.

            Reason: {reason or 'Document does not meet requirements'}

            Please re-upload the correct document to continue with your application.

            Regards,
            Admission Automation System
            """

        return EmailService.send_email(to, subject, body, None, user_id)

    @staticmethod
    def send_payment_confirmation(to, name, amount, receipt_number, user_id=None):
        """Send payment confirmation email"""
        subject = "Payment Successful - Admission Automation System"
        body = f"""
        Dear {name},

        Your payment of ₹{amount} has been processed successfully.

        Receipt Number: {receipt_number}

        You can download your receipt from your dashboard.

        Thank you for your payment.

        Regards,
        Admission Automation System
        """

        html = f"""
        <html>
            <body>
                <h2>Payment Successful!</h2>
                <p>Dear {name},</p>
                <p>Your payment of <strong>₹{amount}</strong> has been processed successfully.</p>
                <p><strong>Receipt Number:</strong> {receipt_number}</p>
                <p>You can download your receipt from your dashboard.</p>
                <p>Thank you for your payment.</p>
                <br>
                <p>Regards,<br>Admission Automation System</p>
            </body>
        </html>
        """

        return EmailService.send_email(to, subject, body, html, user_id)

    @staticmethod
    def send_seat_allotment_notification(to, name, college, course, round_number, user_id=None):
        """Send seat allotment notification"""
        subject = f"Seat Allotted - Round {round_number}"
        body = f"""
        Dear {name},

        Congratulations! You have been allotted a seat in Round {round_number}.

        College: {college}
        Course: {course}

        Please log in to your account to:
        1. View your allotment letter
        2. Accept or reject the seat
        3. Pay admission fee (if accepting)

        Important: You must accept or reject the seat before the deadline.

        Regards,
        Admission Automation System
        """

        html = f"""
        <html>
            <body>
                <h2>Congratulations! Seat Allotted</h2>
                <p>Dear {name},</p>
                <p>You have been allotted a seat in <strong>Round {round_number}</strong>.</p>
                <p><strong>College:</strong> {college}<br>
                <strong>Course:</strong> {course}</p>
                <h3>Next Steps:</h3>
                <ol>
                    <li>Log in to your account</li>
                    <li>View your allotment letter</li>
                    <li>Accept or reject the seat</li>
                    <li>Pay admission fee (if accepting)</li>
                </ol>
                <p style="color: red;"><strong>Important:</strong> You must accept or reject the seat before the deadline.</p>
                <br>
                <p>Regards,<br>Admission Automation System</p>
            </body>
        </html>
        """

        return EmailService.send_email(to, subject, body, html, user_id)
