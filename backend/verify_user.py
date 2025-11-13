"""
Script to verify user email and mobile (bypass OTP verification for testing)
"""
import sys
from app import create_app, db
from app.models import User

def verify_user(email_or_mobile):
    """Verify a user's email and mobile"""
    app = create_app()

    with app.app_context():
        # Find user by email or mobile
        user = User.query.filter(
            (User.email == email_or_mobile.lower()) |
            (User.mobile == email_or_mobile)
        ).first()

        if not user:
            print(f"❌ User not found: {email_or_mobile}")
            return

        # Check if already verified
        if user.is_verified:
            print(f"✓ User {user.email} is already verified")
            return

        # Verify user
        user.email_verified = True
        user.mobile_verified = True
        user.is_verified = True

        db.session.commit()

        print(f"✓ Successfully verified user:")
        print(f"  Email: {user.email}")
        print(f"  Mobile: {user.mobile}")
        print(f"  Role: {user.role.value}")
        print(f"\n✓ User can now login to the system")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python verify_user.py <email_or_mobile>")
        print("Example: python verify_user.py sami@gmail.com")
        print("Example: python verify_user.py 9876543210")
        sys.exit(1)

    verify_user(sys.argv[1])
