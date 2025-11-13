"""
Flask application factory
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.config.config import config
from app.models import db, bcrypt
from app.services.email_service import mail


migrate = Migrate()
jwt = JWTManager()


def create_app(config_name='development'):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # Register blueprints
    from app.routes import auth, student, admin, document, payment, choice, allotment

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(student.bp, url_prefix='/api/student')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(document.bp, url_prefix='/api/documents')
    app.register_blueprint(payment.bp, url_prefix='/api/payment')
    app.register_blueprint(choice.bp, url_prefix='/api/choices')
    app.register_blueprint(allotment.bp, url_prefix='/api/allotment')

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Admission Automation System API is running'}, 200

    @app.route('/')
    def index():
        return {
            'name': app.config['APP_NAME'],
            'version': app.config['APP_VERSION'],
            'status': 'running'
        }, 200

    return app


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad Request', 'message': str(error)}, 400

    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'Insufficient permissions'}, 403

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500
