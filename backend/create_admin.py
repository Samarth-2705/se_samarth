"""
Script to create an admin user
"""
from app import create_app, db
from app.models import User, UserRole
from app.models import bcrypt

def create_admin():
    """Create an admin user"""
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@admission.com').first()

        if admin:
            print("Admin user already exists!")
            print(f"Email: admin@admission.com")
            return

        # Create admin user
        admin = User(
            email='admin@admission.com',
            mobile='9999999999',
            role=UserRole.ADMIN,
            is_verified=True,
            email_verified=True,
            mobile_verified=True
        )

        # Set password
        admin.password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')

        db.session.add(admin)
        db.session.commit()

        print("=" * 50)
        print("Admin user created successfully!")
        print("=" * 50)
        print(f"Email: admin@admission.com")
        print(f"Password: admin123")
        print("=" * 50)
        print("\nYou can now login to the admin panel")


if __name__ == '__main__':
    create_admin()
