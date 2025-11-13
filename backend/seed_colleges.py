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
                'type': 'Government',
                'university': 'Autonomous',
            },
            {
                'name': 'BMS College of Engineering',
                'code': 'BMSCE',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'VTU',
            },
            {
                'name': 'RV College of Engineering',
                'code': 'RVCE',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'VTU',
            },
            {
                'name': 'PES University',
                'code': 'PESU',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'Autonomous',
            },
            {
                'name': 'MS Ramaiah Institute of Technology',
                'code': 'MSRIT',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'VTU',
            },
            {
                'name': 'BMS Institute of Technology',
                'code': 'BMSIT',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'VTU',
            },
            {
                'name': 'Dayananda Sagar College of Engineering',
                'code': 'DSCE',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'VTU',
            },
            {
                'name': 'NIE Institute of Technology',
                'code': 'NIEIT',
                'city': 'Mysore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'VTU',
            },
            {
                'name': 'Manipal Institute of Technology',
                'code': 'MIT',
                'city': 'Manipal',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'Manipal University',
            },
            {
                'name': 'JSS Science and Technology University',
                'code': 'JSSTU',
                'city': 'Mysore',
                'state': 'Karnataka',
                'type': 'Private',
                'university': 'Autonomous',
            }
        ]

        # Sample courses for each college
        courses_template = [
            {
                'name': 'Computer Science and Engineering',
                'code': 'CSE',
                'branch': 'Computer Science and Engineering',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 120,
                'available_seats': 120,
                'general_seats': 60,
                'obc_seats': 30,
                'sc_seats': 18,
                'st_seats': 9,
                'ews_seats': 3,
                'min_rank': 100,
                'max_rank': 5000,
                'tuition_fee': 150000,
                'other_fees': 10000,
            },
            {
                'name': 'Electronics and Communication Engineering',
                'code': 'ECE',
                'branch': 'Electronics and Communication Engineering',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 90,
                'available_seats': 90,
                'general_seats': 45,
                'obc_seats': 22,
                'sc_seats': 14,
                'st_seats': 7,
                'ews_seats': 2,
                'min_rank': 150,
                'max_rank': 6000,
                'tuition_fee': 140000,
                'other_fees': 10000,
            },
            {
                'name': 'Information Science and Engineering',
                'code': 'ISE',
                'branch': 'Information Science and Engineering',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 90,
                'available_seats': 90,
                'general_seats': 45,
                'obc_seats': 22,
                'sc_seats': 14,
                'st_seats': 7,
                'ews_seats': 2,
                'min_rank': 200,
                'max_rank': 7000,
                'tuition_fee': 145000,
                'other_fees': 10000,
            },
            {
                'name': 'Mechanical Engineering',
                'code': 'ME',
                'branch': 'Mechanical Engineering',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 120,
                'available_seats': 120,
                'general_seats': 60,
                'obc_seats': 30,
                'sc_seats': 18,
                'st_seats': 9,
                'ews_seats': 3,
                'min_rank': 300,
                'max_rank': 8000,
                'tuition_fee': 130000,
                'other_fees': 10000,
            },
            {
                'name': 'Civil Engineering',
                'code': 'CE',
                'branch': 'Civil Engineering',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 60,
                'available_seats': 60,
                'general_seats': 30,
                'obc_seats': 15,
                'sc_seats': 9,
                'st_seats': 5,
                'ews_seats': 1,
                'min_rank': 500,
                'max_rank': 10000,
                'tuition_fee': 120000,
                'other_fees': 10000,
            },
            {
                'name': 'Electrical and Electronics Engineering',
                'code': 'EEE',
                'branch': 'Electrical and Electronics Engineering',
                'duration_years': 4,
                'degree': 'B.E.',
                'total_seats': 60,
                'available_seats': 60,
                'general_seats': 30,
                'obc_seats': 15,
                'sc_seats': 9,
                'st_seats': 5,
                'ews_seats': 1,
                'min_rank': 400,
                'max_rank': 9000,
                'tuition_fee': 135000,
                'other_fees': 10000,
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
                    branch=course_template['branch'],
                    duration_years=course_template['duration_years'],
                    degree=course_template['degree'],
                    total_seats=course_template['total_seats'],
                    available_seats=course_template['available_seats'],
                    general_seats=course_template['general_seats'],
                    obc_seats=course_template['obc_seats'],
                    sc_seats=course_template['sc_seats'],
                    st_seats=course_template['st_seats'],
                    ews_seats=course_template['ews_seats'],
                    min_rank=int(course_template['min_rank'] * rank_multiplier),
                    max_rank=int(course_template['max_rank'] * rank_multiplier),
                    tuition_fee=course_template['tuition_fee'],
                    other_fees=course_template['other_fees'],
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
