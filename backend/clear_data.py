"""
Script to clear all data from the database
WARNING: This will delete ALL data including students, payments, allotments, etc.
"""
import sys
from app import create_app, db
from app.models import (
    User, Student, Document, Payment, Choice, Allotment, AllotmentRound,
    College, Course, OTP, AuditLog, UserRole
)

def clear_all_data():
    """Clear all data from database"""
    app = create_app()

    with app.app_context():
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("This includes:")
        print("  - All users (students and admins)")
        print("  - All documents")
        print("  - All payments")
        print("  - All choices")
        print("  - All allotments")
        print("  - All colleges and courses")
        print("  - All audit logs")
        print()

        confirm = input("Are you sure you want to continue? Type 'YES' to confirm: ")

        if confirm != 'YES':
            print("❌ Operation cancelled")
            return

        try:
            # Delete in correct order (respecting foreign keys)
            print("\n🗑️  Deleting data...")

            # Delete allotments first
            allotments_count = Allotment.query.delete()
            print(f"  ✓ Deleted {allotments_count} allotments")

            # Delete allotment rounds
            rounds_count = AllotmentRound.query.delete()
            print(f"  ✓ Deleted {rounds_count} allotment rounds")

            # Delete choices
            choices_count = Choice.query.delete()
            print(f"  ✓ Deleted {choices_count} choices")

            # Delete payments
            payments_count = Payment.query.delete()
            print(f"  ✓ Deleted {payments_count} payments")

            # Delete documents
            documents_count = Document.query.delete()
            print(f"  ✓ Deleted {documents_count} documents")

            # Delete OTPs
            otps_count = OTP.query.delete()
            print(f"  ✓ Deleted {otps_count} OTPs")

            # Delete students
            students_count = Student.query.delete()
            print(f"  ✓ Deleted {students_count} students")

            # Delete audit logs
            logs_count = AuditLog.query.delete()
            print(f"  ✓ Deleted {logs_count} audit logs")

            # Delete users (except admins if you want to keep them)
            users_count = User.query.filter(User.role != UserRole.ADMIN).delete()
            print(f"  ✓ Deleted {users_count} users (kept admins)")

            db.session.commit()

            print("\n✅ All student data has been cleared successfully!")
            print("📝 Note: Admin accounts and college/course data have been preserved")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")

def clear_everything():
    """Clear EVERYTHING including colleges and courses"""
    app = create_app()

    with app.app_context():
        print("⚠️  DANGER: This will delete EVERYTHING from the database!")
        print()

        confirm = input("Are you sure you want to delete ALL data including colleges? Type 'DELETE EVERYTHING' to confirm: ")

        if confirm != 'DELETE EVERYTHING':
            print("❌ Operation cancelled")
            return

        try:
            print("\n🗑️  Deleting all data...")

            # Delete everything
            Allotment.query.delete()
            AllotmentRound.query.delete()
            Choice.query.delete()
            Payment.query.delete()
            Document.query.delete()
            OTP.query.delete()
            Student.query.delete()
            User.query.delete()
            Course.query.delete()
            College.query.delete()
            AuditLog.query.delete()

            db.session.commit()

            print("✅ Database has been completely cleared!")
            print("📝 You can now run seed_colleges.py and create_admin.py to start fresh")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Delete everything including colleges and courses
        clear_everything()
    else:
        # Delete only student data, keep colleges and admins
        clear_all_data()
        print("\n💡 Tip: Use 'python clear_data.py --all' to delete colleges/courses too")
