"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models import db, User, Student, OTP, OTPPurpose, UserRole, AuditLog
from app.utils.validators import validate_email, validate_mobile, validate_password
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new student user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'mobile', 'password', 'first_name', 'last_name',
                         'date_of_birth', 'gender', 'exam_type', 'exam_rank', 'exam_roll_number', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate email
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate mobile
        if not validate_mobile(data['mobile']):
            return jsonify({'error': 'Invalid mobile number'}), 400

        # Validate password
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400

        # Check if user already exists
        if User.query.filter_by(email=data['email'].lower()).first():
            return jsonify({'error': 'Email already registered'}), 409

        if User.query.filter_by(mobile=data['mobile']).first():
            return jsonify({'error': 'Mobile number already registered'}), 409

        # Check if exam roll number already exists
        if Student.query.filter_by(exam_roll_number=data['exam_roll_number']).first():
            return jsonify({'error': 'Exam roll number already registered'}), 409

        # Create user
        user = User(
            email=data['email'],
            mobile=data['mobile'],
            password=data['password'],
            role=UserRole.STUDENT
        )

        db.session.add(user)
        db.session.flush()  # Get user ID

        # Create student profile
        student = Student(
            user_id=user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data.get('middle_name'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            gender=data['gender'],
            exam_type=data['exam_type'],
            exam_rank=data['exam_rank'],
            exam_roll_number=data['exam_roll_number'],
            category=data['category'],
            domicile_state=data.get('domicile_state', 'Karnataka'),
            is_pwd=data.get('is_pwd', False)
        )

        db.session.add(student)

        # Generate OTP for email verification
        email_otp = OTP.create_otp(
            purpose=OTPPurpose.EMAIL_VERIFICATION,
            email=user.email,
            user_id=user.id
        )
        db.session.add(email_otp)

        # Generate OTP for mobile verification
        mobile_otp = OTP.create_otp(
            purpose=OTPPurpose.MOBILE_VERIFICATION,
            mobile=user.mobile,
            user_id=user.id
        )
        db.session.add(mobile_otp)

        db.session.commit()

        # Send OTPs
        EmailService.send_otp_email(user.email, email_otp.code, 'email verification', user.id)
        SMSService.send_otp_sms(user.mobile, mobile_otp.code, user.id)

        # Log action
        AuditLog.log_action(
            user_id=user.id,
            action='user_registered',
            entity_type='User',
            entity_id=user.id,
            description='New user registered',
            ip_address=request.remote_addr,
            request_method=request.method,
            request_path=request.path
        )
        db.session.commit()

        return jsonify({
            'message': 'Registration successful. Please verify your email and mobile.',
            'user_id': user.id,
            'email': user.email,
            'mobile': user.mobile
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP for email or mobile"""
    try:
        data = request.get_json()

        if 'otp' not in data or 'user_id' not in data or 'type' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Determine OTP purpose
        purpose = (OTPPurpose.EMAIL_VERIFICATION if data['type'] == 'email'
                  else OTPPurpose.MOBILE_VERIFICATION)

        # Find OTP
        otp = OTP.query.filter_by(
            user_id=user.id,
            purpose=purpose,
            is_used=False
        ).order_by(OTP.created_at.desc()).first()

        if not otp:
            return jsonify({'error': 'OTP not found or already used'}), 404

        # Verify OTP
        if otp.verify(data['otp']):
            # Update user verification status
            if purpose == OTPPurpose.EMAIL_VERIFICATION:
                user.email_verified = True
            else:
                user.mobile_verified = True

            # Check if both are verified
            if user.email_verified and user.mobile_verified:
                user.is_verified = True

            db.session.commit()

            return jsonify({
                'message': 'OTP verified successfully',
                'verified': True,
                'email_verified': user.email_verified,
                'mobile_verified': user.mobile_verified
            }), 200
        else:
            db.session.commit()
            return jsonify({'error': 'Invalid or expired OTP'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP"""
    try:
        data = request.get_json()

        if 'user_id' not in data or 'type' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Determine OTP purpose
        purpose = (OTPPurpose.EMAIL_VERIFICATION if data['type'] == 'email'
                  else OTPPurpose.MOBILE_VERIFICATION)

        # Create new OTP
        if data['type'] == 'email':
            otp = OTP.create_otp(purpose=purpose, email=user.email, user_id=user.id)
            db.session.add(otp)
            db.session.commit()
            EmailService.send_otp_email(user.email, otp.code, 'email verification', user.id)
        else:
            otp = OTP.create_otp(purpose=purpose, mobile=user.mobile, user_id=user.id)
            db.session.add(otp)
            db.session.commit()
            SMSService.send_otp_sms(user.mobile, otp.code, user.id)

        return jsonify({'message': 'OTP sent successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()

        if 'identifier' not in data or 'password' not in data:
            return jsonify({'error': 'Missing credentials'}), 400

        # Find user by email or mobile
        user = User.query.filter(
            (User.email == data['identifier'].lower()) |
            (User.mobile == data['identifier'])
        ).first()

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check if account is locked
        if user.is_locked():
            return jsonify({'error': 'Account is locked. Please try again later.'}), 403

        # Verify password
        if not user.check_password(data['password']):
            user.increment_failed_login()

            # Lock account if max attempts reached
            if user.failed_login_attempts >= 5:
                user.lock_account(1800)  # Lock for 30 minutes

            db.session.commit()
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check if user is verified
        if not user.is_verified:
            return jsonify({'error': 'Please verify your email and mobile first'}), 403

        # Reset failed login attempts
        user.reset_failed_login()
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Log action
        AuditLog.log_action(
            user_id=user.id,
            action='user_login',
            entity_type='User',
            entity_id=user.id,
            description='User logged in',
            ip_address=request.remote_addr,
            request_method=request.method,
            request_path=request.path
        )
        db.session.commit()

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)

        return jsonify({'access_token': access_token}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = user.to_dict()

        # Include student profile if user is a student
        if user.role == UserRole.STUDENT and user.student:
            user_data['student'] = user.student.to_dict()

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()

        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=data['email'].lower()).first()

        if not user:
            # Don't reveal if email exists
            return jsonify({'message': 'If the email exists, a reset code has been sent'}), 200

        # Create OTP for password reset
        otp = OTP.create_otp(
            purpose=OTPPurpose.PASSWORD_RESET,
            email=user.email,
            user_id=user.id
        )
        db.session.add(otp)
        db.session.commit()

        # Send OTP
        EmailService.send_otp_email(user.email, otp.code, 'password reset', user.id)

        return jsonify({'message': 'If the email exists, a reset code has been sent'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using OTP"""
    try:
        data = request.get_json()

        required_fields = ['email', 'otp', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        user = User.query.filter_by(email=data['email'].lower()).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Validate new password
        is_valid, message = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400

        # Find OTP
        otp = OTP.query.filter_by(
            user_id=user.id,
            purpose=OTPPurpose.PASSWORD_RESET,
            is_used=False
        ).order_by(OTP.created_at.desc()).first()

        if not otp or not otp.verify(data['otp']):
            return jsonify({'error': 'Invalid or expired OTP'}), 400

        # Reset password
        user.set_password(data['new_password'])
        db.session.commit()

        # Log action
        AuditLog.log_action(
            user_id=user.id,
            action='password_reset',
            entity_type='User',
            entity_id=user.id,
            description='Password reset successfully',
            ip_address=request.remote_addr
        )
        db.session.commit()

        return jsonify({'message': 'Password reset successful'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
