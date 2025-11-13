"""
Script to update admission_confirmed status for students who have frozen their seats
"""
from app import create_app, db
from app.models import Student, Allotment, AllotmentStatus

def fix_admission_confirmed():
    """Update admission_confirmed for students with frozen seats"""
    app = create_app()

    with app.app_context():
        # Find all students with frozen seats
        frozen_allotments = Allotment.query.filter_by(
            status=AllotmentStatus.ACCEPTED_FROZEN
        ).all()

        updated_count = 0

        for allotment in frozen_allotments:
            student = allotment.student
            if not student.admission_confirmed:
                student.admission_confirmed = True
                updated_count += 1
                print(f"Updated student {student.id} ({student.full_name}) - admission confirmed")

        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully updated {updated_count} student(s)")
        else:
            print("\nNo updates needed. All students with frozen seats already have admission_confirmed set.")

if __name__ == '__main__':
    fix_admission_confirmed()
