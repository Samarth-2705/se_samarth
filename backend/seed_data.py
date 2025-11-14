"""
Seed the database with initial data:
- Admin user
- Sample colleges
- Sample courses
"""
from datetime import datetime
from app import create_app, db
from app.models import User, UserRole, College, Course

def seed_database():
    """Seed database with initial data"""
    app = create_app()

    with app.app_context():
        print("Starting database seeding...")

        # Check if admin already exists
        admin = User.query.filter_by(email='admin@admission.com').first()
        if not admin:
            print("\n1. Creating Admin User...")
            admin = User(
                email='admin@admission.com',
                mobile='9999999999',
                password='Admin@123',  # Remember to change this in production!
                role=UserRole.ADMIN
            )
            admin.email_verified = True
            admin.mobile_verified = True
            admin.is_verified = True
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created")
            print(f"  Email: admin@admission.com")
            print(f"  Password: Admin@123")
            print(f"  ⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("\n1. Admin user already exists")

        # Check if colleges exist
        existing_colleges = College.query.count()
        if existing_colleges == 0:
            print("\n2. Creating Sample Colleges and Courses...")

            # Sample colleges data
            colleges_data = [
                {
                    'name': 'National Institute of Technology Karnataka',
                    'code': 'NITK',
                    'city': 'Surathkal',
                    'state': 'Karnataka',
                    'type': 'Government'
                },
                {
                    'name': 'RV College of Engineering',
                    'code': 'RVCE',
                    'city': 'Bangalore',
                    'state': 'Karnataka',
                    'type': 'Private'
                },
                {
                    'name': 'BMS College of Engineering',
                    'code': 'BMSCE',
                    'city': 'Bangalore',
                    'state': 'Karnataka',
                    'type': 'Private'
                },
                {
                    'name': 'PES University',
                    'code': 'PESU',
                    'city': 'Bangalore',
                    'state': 'Karnataka',
                    'type': 'Private'
                },
                {
                    'name': 'MS Ramaiah Institute of Technology',
                    'code': 'MSRIT',
                    'city': 'Bangalore',
                    'state': 'Karnataka',
                    'type': 'Private'
                }
            ]

            # Course branches
            branches_data = [
                {'name': 'Computer Science and Engineering', 'code': 'CSE', 'degree': 'B.E.', 'seats': 120, 'fee': 200000},
                {'name': 'Information Science and Engineering', 'code': 'ISE', 'degree': 'B.E.', 'seats': 90, 'fee': 180000},
                {'name': 'Electronics and Communication Engineering', 'code': 'ECE', 'degree': 'B.E.', 'seats': 100, 'fee': 170000},
                {'name': 'Mechanical Engineering', 'code': 'ME', 'degree': 'B.E.', 'seats': 100, 'fee': 150000},
                {'name': 'Civil Engineering', 'code': 'CE', 'degree': 'B.E.', 'seats': 80, 'fee': 140000},
            ]

            total_colleges = 0
            total_courses = 0

            for college_data in colleges_data:
                # Create college
                college = College(
                    name=college_data['name'],
                    code=college_data['code'],
                    city=college_data['city'],
                    state=college_data['state'],
                    type=college_data['type'],
                    university='Autonomous',
                    is_active=True
                )
                db.session.add(college)
                db.session.flush()
                total_colleges += 1

                # Create courses for this college
                for i, branch in enumerate(branches_data):
                    # Not all colleges offer all branches
                    if i < 3 or college_data['code'] in ['NITK', 'RVCE']:  # Top colleges offer all branches
                        course = Course(
                            college_id=college.id,
                            code=branch['code'],
                            name=branch['name'],
                            degree=branch['degree'],
                            branch=branch['name'],
                            duration_years=4,
                            total_seats=branch['seats'],
                            available_seats=branch['seats'],
                            general_seats=int(branch['seats'] * 0.5),
                            obc_seats=int(branch['seats'] * 0.27),
                            sc_seats=int(branch['seats'] * 0.15),
                            st_seats=int(branch['seats'] * 0.075),
                            ews_seats=int(branch['seats'] * 0.005),
                            tuition_fee=branch['fee'],
                            other_fees=10000,
                            min_rank=1000 if college_data['code'] == 'NITK' else 5000,
                            max_rank=10000 if college_data['code'] == 'NITK' else 50000,
                            is_active=True
                        )
                        db.session.add(course)
                        total_courses += 1

            db.session.commit()
            print(f"✓ Created {total_colleges} colleges")
            print(f"✓ Created {total_courses} courses")
        else:
            print(f"\n2. Database already has {existing_colleges} colleges")

        print("\n✓ Database seeding completed successfully!")
        print("\n" + "="*60)
        print("ADMIN LOGIN CREDENTIALS:")
        print("="*60)
        print("Email:    admin@admission.com")
        print("Password: Admin@123")
        print("="*60)
        print("\n⚠️  IMPORTANT: Change the admin password after first login!")

if __name__ == '__main__':
    seed_database()
