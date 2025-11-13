"""
Script to populate database with sample colleges and courses
"""
import sys
from app import create_app, db
from app.models import College, Course

def seed_colleges_and_courses(force=False):
    """Add sample colleges and courses to the database"""

    app = create_app()
    with app.app_context():
        # Check if colleges already exist
        existing_colleges = College.query.count()

        if existing_colleges > 0 and not force:
            print(f"Database already has {existing_colleges} colleges.")
            print("Run with --force to clear and re-seed, or --add to add more colleges")
            return

        if force:
            print(f"Clearing {existing_colleges} existing colleges...")
            # Delete existing courses first (foreign key constraint)
            Course.query.delete()
            College.query.delete()
            db.session.commit()
            print("Existing data cleared.")

        print("Seeding colleges and courses...")

        # Sample colleges
        colleges_data = [
            {
                'name': 'National Institute of Technology Karnataka',
                'code': 'NITK',
                'city': 'Surathkal',
                'state': 'Karnataka',
                'type': 'government',
                'affiliation': 'Autonomous',
                'established_year': 1960,
                'is_active': True
            },
            {
                'name': 'BMS College of Engineering',
                'code': 'BMSCE',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'VTU',
                'established_year': 1946,
                'is_active': True
            },
            {
                'name': 'RV College of Engineering',
                'code': 'RVCE',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'VTU',
                'established_year': 1963,
                'is_active': True
            },
            {
                'name': 'PES University',
                'code': 'PESU',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'Autonomous',
                'established_year': 1988,
                'is_active': True
            },
            {
                'name': 'MS Ramaiah Institute of Technology',
                'code': 'MSRIT',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'VTU',
                'established_year': 1962,
                'is_active': True
            },
            {
                'name': 'BMS Institute of Technology',
                'code': 'BMSIT',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'VTU',
                'established_year': 2002,
                'is_active': True
            },
            {
                'name': 'Dayananda Sagar College of Engineering',
                'code': 'DSCE',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'VTU',
                'established_year': 1979,
                'is_active': True
            },
            {
                'name': 'NIE Institute of Technology',
                'code': 'NIEIT',
                'city': 'Mysore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'VTU',
                'established_year': 1946,
                'is_active': True
            },
            {
                'name': 'Manipal Institute of Technology',
                'code': 'MIT',
                'city': 'Manipal',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'Manipal University',
                'established_year': 1957,
                'is_active': True
            },
            {
                'name': 'JSS Science and Technology University',
                'code': 'JSSTU',
                'city': 'Mysore',
                'state': 'Karnataka',
                'type': 'private',
                'affiliation': 'Autonomous',
                'established_year': 1963,
                'is_active': True
            }
        ]

        # Sample courses for each college
        courses_template = [
            {
                'name': 'Computer Science and Engineering',
                'code': 'CSE',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 120,
                'available_seats': 120,
                'min_rank': 100,
                'max_rank': 5000,
                'fee_per_year': 150000,
                'is_active': True
            },
            {
                'name': 'Electronics and Communication Engineering',
                'code': 'ECE',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 90,
                'available_seats': 90,
                'min_rank': 150,
                'max_rank': 6000,
                'fee_per_year': 140000,
                'is_active': True
            },
            {
                'name': 'Information Science and Engineering',
                'code': 'ISE',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 90,
                'available_seats': 90,
                'min_rank': 200,
                'max_rank': 7000,
                'fee_per_year': 145000,
                'is_active': True
            },
            {
                'name': 'Mechanical Engineering',
                'code': 'ME',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 120,
                'available_seats': 120,
                'min_rank': 300,
                'max_rank': 8000,
                'fee_per_year': 130000,
                'is_active': True
            },
            {
                'name': 'Civil Engineering',
                'code': 'CE',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 60,
                'available_seats': 60,
                'min_rank': 500,
                'max_rank': 10000,
                'fee_per_year': 120000,
                'is_active': True
            },
            {
                'name': 'Electrical and Electronics Engineering',
                'code': 'EEE',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 60,
                'available_seats': 60,
                'min_rank': 400,
                'max_rank': 9000,
                'fee_per_year': 135000,
                'is_active': True
            }
        ]

        # Create colleges and courses
        for i, college_data in enumerate(colleges_data):
            college = College(**college_data)
            db.session.add(college)
            db.session.flush()  # Get college ID

            print(f"Added college: {college.name}")

            # Adjust rank ranges based on college prestige
            rank_multiplier = 1.0 + (i * 0.3)  # Each college has slightly higher rank requirements

            # Add courses to this college
            for course_template in courses_template:
                course = Course(
                    college_id=college.id,
                    name=course_template['name'],
                    code=course_template['code'],
                    duration_years=course_template['duration_years'],
                    degree=course_template['degree'],
                    total_seats=course_template['total_seats'],
                    available_seats=course_template['available_seats'],
                    min_rank=int(course_template['min_rank'] * rank_multiplier),
                    max_rank=int(course_template['max_rank'] * rank_multiplier),
                    fee_per_year=course_template['fee_per_year'],
                    is_active=course_template['is_active']
                )
                db.session.add(course)

            print(f"  Added {len(courses_template)} courses")

        db.session.commit()
        print("\n" + "="*50)
        print("Seeding completed successfully!")
        print(f"Added {len(colleges_data)} colleges with {len(courses_template)} courses each")
        print(f"Total courses: {len(colleges_data) * len(courses_template)}")
        print("="*50)


if __name__ == '__main__':
    force = '--force' in sys.argv or '--add' in sys.argv
    seed_colleges_and_courses(force=force)
