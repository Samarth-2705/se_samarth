"""
Document management routes
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.models import db, User, Document, DocumentType, DocumentStatus, UserRole, AuditLog
from app.utils.validators import validate_file_extension, validate_file_size, sanitize_filename
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

bp = Blueprint('document', __name__)


@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get document type
        document_type = request.form.get('document_type')
        if not document_type:
            return jsonify({'error': 'Document type is required'}), 400

        try:
            document_type = DocumentType(document_type)
        except ValueError:
            return jsonify({'error': 'Invalid document type'}), 400

        # Validate file extension
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        if not validate_file_extension(file.filename, allowed_extensions):
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        max_size = current_app.config['MAX_FILE_SIZE']
        if not validate_file_size(file_size, max_size):
            return jsonify({'error': f'File size exceeds maximum limit of {max_size / 1024 / 1024}MB'}), 400

        # Sanitize filename
        original_filename = secure_filename(file.filename)
        filename = sanitize_filename(original_filename)

        # Create upload directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        student_folder = os.path.join(upload_folder, f'student_{student.id}')
        os.makedirs(student_folder, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{document_type.value}_{timestamp}.{file_extension}"
        file_path = os.path.join(student_folder, unique_filename)

        # Save file
        file.save(file_path)

        # Create document record
        document = Document(
            student_id=student.id,
            document_type=document_type,
            file_name=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_extension=file_extension,
            mime_type=file.content_type or 'application/octet-stream',
            status=DocumentStatus.PENDING
        )

        db.session.add(document)
        db.session.commit()

        # Log action
        AuditLog.log_action(
            user_id=user.id,
            action='document_uploaded',
            entity_type='Document',
            entity_id=document.id,
            description=f'Document uploaded: {document_type.value}'
        )
        db.session.commit()

        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Document upload failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/list', methods=['GET'])
@jwt_required()
def list_documents():
    """List user's documents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.STUDENT:
            return jsonify({'error': 'Unauthorized'}), 403

        student = user.student
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404

        documents = Document.query.filter_by(student_id=student.id)\
            .order_by(Document.uploaded_at.desc()).all()

        return jsonify({
            'documents': [doc.to_dict() for doc in documents]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:document_id>/download', methods=['GET'])
@jwt_required()
def download_document(document_id):
    """Download a document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        # Check permissions
        if user.role == UserRole.STUDENT:
            if not user.student or document.student_id != user.student.id:
                return jsonify({'error': 'Unauthorized'}), 403
        elif user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized'}), 403

        # Check if file exists
        if not os.path.exists(document.file_path):
            return jsonify({'error': 'File not found on server'}), 404

        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.file_name
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:document_id>/verify', methods=['PUT'])
@jwt_required()
def verify_document(document_id):
    """Verify or reject a document (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        document = Document.query.get(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404

        data = request.get_json()
        action = data.get('action')  # 'verify' or 'reject'
        reason = data.get('reason', '')

        if action == 'verify':
            document.status = DocumentStatus.VERIFIED
            document.verified_by = user.id
            document.verified_at = datetime.utcnow()

            # Check if all required documents are verified
            student = document.student
            required_documents = [
                DocumentType.MARKS_CARD_10TH,
                DocumentType.MARKS_CARD_12TH,
                DocumentType.RANK_CARD
            ]

            all_verified = True
            for doc_type in required_documents:
                doc = Document.query.filter_by(
                    student_id=student.id,
                    document_type=doc_type,
                    status=DocumentStatus.VERIFIED
                ).first()

                if not doc:
                    all_verified = False
                    break

            if all_verified:
                student.documents_verified = True

            # Send notification
            if student.user:
                EmailService.send_document_verification_notification(
                    student.user.email,
                    student.full_name,
                    document.document_type.value,
                    'verified',
                    user_id=student.user_id
                )
                SMSService.send_document_verification_sms(
                    student.user.mobile,
                    student.full_name,
                    document.document_type.value,
                    'verified',
                    user_id=student.user_id
                )

        elif action == 'reject':
            document.status = DocumentStatus.REJECTED
            document.verified_by = user.id
            document.verified_at = datetime.utcnow()
            document.rejection_reason = reason

            # Send notification
            student = document.student
            if student.user:
                EmailService.send_document_verification_notification(
                    student.user.email,
                    student.full_name,
                    document.document_type.value,
                    'rejected',
                    reason,
                    user_id=student.user_id
                )
                SMSService.send_document_verification_sms(
                    student.user.mobile,
                    student.full_name,
                    document.document_type.value,
                    'rejected',
                    user_id=student.user_id
                )

        else:
            return jsonify({'error': 'Invalid action'}), 400

        db.session.commit()

        # Log action
        AuditLog.log_action(
            user_id=user.id,
            action=f'document_{action}ed',
            entity_type='Document',
            entity_id=document.id,
            description=f'Document {action}ed: {document.document_type.value}'
        )
        db.session.commit()

        return jsonify({
            'message': f'Document {action}ed successfully',
            'document': document.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_documents():
    """Get pending documents for verification (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Unauthorized - Admin access required'}), 403

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        pagination = Document.query.filter_by(status=DocumentStatus.PENDING)\
            .order_by(Document.uploaded_at).paginate(
                page=page, per_page=per_page, error_out=False
            )

        documents = []
        for doc in pagination.items:
            doc_dict = doc.to_dict()
            doc_dict['student'] = doc.student.to_dict() if doc.student else None
            documents.append(doc_dict)

        return jsonify({
            'documents': documents,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
