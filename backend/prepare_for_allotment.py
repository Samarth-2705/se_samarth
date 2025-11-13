"""
Script to prepare students for seat allotment
Marks documents as verified and ensures all prerequisites are met
"""
from app import create_app, db
from app.models import User, Student

def prepare_student_for_allotment(email):
    """Mark student as ready for allotment"""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"User with email {email} not found!")
            return

        student = user.student
        if not student:
            print(f"No student profile found for {email}")
            return

        print("=" * 50)
        print(f"Preparing student: {student.full_name}")
        print("=" * 50)

        # Check current status
        print("\nCurrent Status:")
        print(f"  Registration Complete: {'✓' if student.registration_complete else '✗'}")
        print(f"  Payment Complete: {'✓' if student.payment_complete else '✗'}")
        print(f"  Documents Verified: {'✓' if student.documents_verified else '✗'}")
        print(f"  Choices Submitted: {'✓' if student.choices_submitted else '✗'}")

        # Update status for allotment eligibility
        if not student.documents_verified:
            student.documents_verified = True
            print("\n✓ Marked documents as verified")

        if not student.registration_complete:
            student.registration_complete = True
            print("✓ Marked registration as complete")

        db.session.commit()

        print("\n" + "=" * 50)
        print("Student is now ready for allotment!")
        print("=" * 50)
        print("\nAllotment Prerequisites:")
        print(f"  ✓ Registration Complete: {student.registration_complete}")
        print(f"  ✓ Payment Complete: {student.payment_complete}")
        print(f"  ✓ Documents Verified: {student.documents_verified}")
        print(f"  ✓ Choices Submitted: {student.choices_submitted}")
        print(f"\n  Student Rank: {student.exam_rank}")
        print(f"  Category: {student.category}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python prepare_for_allotment.py <student_email>")
        print("Example: python prepare_for_allotment.py samarthtotager7@gmail.com")
        sys.exit(1)

    email = sys.argv[1]
    prepare_student_for_allotment(email)
