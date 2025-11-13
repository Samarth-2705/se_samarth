"""
Application entry point
"""
import os
from app import create_app, db
from app.models import User, Student, Document, College, Course

# Create Flask application
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Document': Document,
        'College': College,
        'Course': Course
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def seed_db():
    """Seed the database with sample data"""
    from datetime import datetime, timedelta

    # Create sample colleges and courses
    college1 = College(
        code='COL001',
        name='PES University',
        type='Private',
        city='Bangalore',
        state='Karnataka',
        email='info@pes.edu',
        website='https://pes.edu'
    )

    college2 = College(
        code='COL002',
        name='RV College of Engineering',
        type='Private',
        city='Bangalore',
        state='Karnataka',
        email='info@rvce.edu.in',
        website='https://rvce.edu.in'
    )

    db.session.add_all([college1, college2])
    db.session.commit()

    # Create sample courses
    course1 = Course(
        college_id=college1.id,
        code='CSE',
        name='Computer Science and Engineering',
        degree='B.E.',
        branch='Computer Science',
        total_seats=120,
        available_seats=120,
        general_seats=60,
        obc_seats=30,
        sc_seats=15,
        st_seats=10,
        ews_seats=5,
        tuition_fee=250000,
        other_fees=10000,
        min_rank=1,
        max_rank=5000
    )

    course2 = Course(
        college_id=college1.id,
        code='ECE',
        name='Electronics and Communication Engineering',
        degree='B.E.',
        branch='Electronics',
        total_seats=90,
        available_seats=90,
        general_seats=45,
        obc_seats=22,
        sc_seats=12,
        st_seats=8,
        ews_seats=3,
        tuition_fee=230000,
        other_fees=10000,
        min_rank=1,
        max_rank=8000
    )

    course3 = Course(
        college_id=college2.id,
        code='CSE',
        name='Computer Science and Engineering',
        degree='B.E.',
        branch='Computer Science',
        total_seats=150,
        available_seats=150,
        general_seats=75,
        obc_seats=37,
        sc_seats=18,
        st_seats=12,
        ews_seats=8,
        tuition_fee=220000,
        other_fees=8000,
        min_rank=1,
        max_rank=6000
    )

    db.session.add_all([course1, course2, course3])
    db.session.commit()

    print("Database seeded successfully!")
    print(f"Created {College.query.count()} colleges")
    print(f"Created {Course.query.count()} courses")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
