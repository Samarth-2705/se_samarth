"""
Unit Tests for Admission Automation System
Tests individual functions and methods in isolation
"""
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Student, UserRole, Course, College, Choice, Allotment, AllotmentStatus, Payment, PaymentStatus, PaymentType

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing"""
    with app.app_context():
        user = User(
            email='test@example.com',
            mobile='9876543210',
            password='password123',
            role=UserRole.STUDENT
        )
        user.email_verified = True
        user.mobile_verified = True
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def sample_student(app, sample_user):
    """Create a sample student for testing"""
    with app.app_context():
        student = Student(
            user_id=sample_user.id,
            first_name='John',
            last_name='Doe',
            date_of_birth=datetime(2000, 1, 1).date(),
            gender='Male',
            exam_type='JEE',
            exam_rank=1500,
            exam_roll_number='JEE2024001',
            category='General'
        )
        db.session.add(student)
        db.session.commit()
        return student

@pytest.fixture
def sample_college(app):
    """Create a sample college for testing"""
    with app.app_context():
        college = College(
            name='Test Institute of Technology',
            code='TIT',
            city='Bangalore',
            state='Karnataka',
            type='Government',
            university='Autonomous'
        )
        db.session.add(college)
        db.session.commit()
        return college

@pytest.fixture
def sample_course(app, sample_college):
    """Create a sample course for testing"""
    with app.app_context():
        course = Course(
            college_id=sample_college.id,
            name='Computer Science and Engineering',
            code='CSE',
            branch='Computer Science',
            duration_years=4,
            degree='B.E.',
            total_seats=120,
            available_seats=120,
            general_seats=60,
            obc_seats=30,
            sc_seats=18,
            st_seats=9,
            ews_seats=3,
            min_rank=100,
            max_rank=5000,
            tuition_fee=150000,
            other_fees=10000
        )
        db.session.add(course)
        db.session.commit()
        return course


class TestUserModel:
    """Unit tests for User model"""

    def test_user_creation(self, app):
        """Test user can be created"""
        with app.app_context():
            user = User(
                email='newuser@test.com',
                mobile='9999999999',
                password='testpass123',
                role=UserRole.STUDENT
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.email == 'newuser@test.com'
            assert user.mobile == '9999999999'
            assert user.role == UserRole.STUDENT
            assert user.is_verified == False

    def test_password_hashing(self, app):
        """Test password is hashed correctly"""
        with app.app_context():
            user = User(
                email='test@test.com',
                mobile='9999999999',
                password='mypassword',
                role=UserRole.STUDENT
            )

            # Password should be hashed
            assert user.password_hash != 'mypassword'
            # Should be able to verify password
            assert user.check_password('mypassword') == True
            assert user.check_password('wrongpassword') == False

    def test_user_verification(self, app, sample_user):
        """Test user verification status"""
        with app.app_context():
            user = User.query.get(sample_user.id)
            assert user.email_verified == True
            assert user.mobile_verified == True
            assert user.is_verified == True


class TestStudentModel:
    """Unit tests for Student model"""

    def test_student_creation(self, app, sample_user):
        """Test student profile can be created"""
        with app.app_context():
            student = Student(
                user_id=sample_user.id,
                first_name='Jane',
                last_name='Smith',
                date_of_birth=datetime(2001, 5, 15).date(),
                gender='Female',
                exam_type='JEE',
                exam_rank=2000,
                exam_roll_number='JEE2024002',
                category='OBC'
            )
            db.session.add(student)
            db.session.commit()

            assert student.id is not None
            assert student.full_name == 'Jane Smith'
            assert student.exam_rank == 2000
            assert student.category == 'OBC'

    def test_student_full_name(self, app, sample_student):
        """Test full name property"""
        with app.app_context():
            student = Student.query.get(sample_student.id)
            assert student.full_name == 'John Doe'

    def test_student_application_status(self, app, sample_student):
        """Test application status property"""
        with app.app_context():
            student = Student.query.get(sample_student.id)

            # Initially incomplete
            assert student.application_status == 'incomplete'

            # Mark as complete
            student.registration_complete = True
            student.payment_complete = True
            student.documents_verified = True
            student.choices_submitted = True
            db.session.commit()

            assert student.application_status == 'complete'


class TestCollegeAndCourseModels:
    """Unit tests for College and Course models"""

    def test_college_creation(self, app):
        """Test college can be created"""
        with app.app_context():
            college = College(
                name='National Institute of Technology',
                code='NIT',
                city='Mumbai',
                state='Maharashtra',
                type='Government',
                university='Autonomous'
            )
            db.session.add(college)
            db.session.commit()

            assert college.id is not None
            assert college.name == 'National Institute of Technology'
            assert college.is_active == True

    def test_course_creation(self, app, sample_college):
        """Test course can be created"""
        with app.app_context():
            course = Course(
                college_id=sample_college.id,
                name='Mechanical Engineering',
                code='ME',
                branch='Mechanical',
                total_seats=100,
                available_seats=100,
                min_rank=500,
                max_rank=3000,
                tuition_fee=120000
            )
            db.session.add(course)
            db.session.commit()

            assert course.id is not None
            assert course.name == 'Mechanical Engineering'
            assert course.total_seats == 100

    def test_course_college_relationship(self, app, sample_course, sample_college):
        """Test course-college relationship"""
        with app.app_context():
            course = Course.query.get(sample_course.id)
            college = College.query.get(sample_college.id)

            assert course.college.id == college.id
            assert course in college.courses


class TestChoiceModel:
    """Unit tests for Choice model"""

    def test_choice_creation(self, app, sample_student, sample_course):
        """Test choice can be created"""
        with app.app_context():
            choice = Choice(
                student_id=sample_student.id,
                course_id=sample_course.id,
                preference_order=1
            )
            db.session.add(choice)
            db.session.commit()

            assert choice.id is not None
            assert choice.preference_order == 1
            assert choice.is_locked == False

    def test_choice_to_dict(self, app, sample_student, sample_course):
        """Test choice to_dict method"""
        with app.app_context():
            choice = Choice(
                student_id=sample_student.id,
                course_id=sample_course.id,
                preference_order=1
            )
            db.session.add(choice)
            db.session.commit()

            choice_dict = choice.to_dict(include_course=True, include_college=True)

            assert choice_dict['preference_order'] == 1
            assert 'course' in choice_dict
            assert 'college' in choice_dict


class TestPaymentModel:
    """Unit tests for Payment model"""

    def test_payment_creation(self, app, sample_student):
        """Test payment can be created"""
        with app.app_context():
            payment = Payment(
                student_id=sample_student.id,
                payment_type=PaymentType.APPLICATION_FEE,
                amount=500,
                currency='INR',
                status=PaymentStatus.INITIATED,
                gateway_name='razorpay'
            )
            db.session.add(payment)
            db.session.commit()

            assert payment.id is not None
            assert payment.amount == 500
            assert payment.status == PaymentStatus.INITIATED

    def test_payment_status_update(self, app, sample_student):
        """Test payment status can be updated"""
        with app.app_context():
            payment = Payment(
                student_id=sample_student.id,
                payment_type=PaymentType.APPLICATION_FEE,
                amount=500,
                currency='INR',
                status=PaymentStatus.INITIATED,
                gateway_name='razorpay'
            )
            db.session.add(payment)
            db.session.commit()

            # Update status
            payment.status = PaymentStatus.SUCCESS
            payment.gateway_payment_id = 'pay_123456'
            db.session.commit()

            assert payment.status == PaymentStatus.SUCCESS
            assert payment.gateway_payment_id == 'pay_123456'


class TestAllotmentModel:
    """Unit tests for Allotment model"""

    def test_allotment_creation(self, app, sample_student, sample_course):
        """Test allotment can be created"""
        with app.app_context():
            from app.models import AllotmentRound

            # Create allotment round
            round = AllotmentRound(
                round_number=1,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                acceptance_deadline=datetime.utcnow() + timedelta(days=10)
            )
            db.session.add(round)
            db.session.commit()

            # Create allotment
            allotment = Allotment(
                student_id=sample_student.id,
                course_id=sample_course.id,
                round_id=round.id,
                allotted_rank=1500,
                allotted_category='General',
                status=AllotmentStatus.ALLOTTED
            )
            db.session.add(allotment)
            db.session.commit()

            assert allotment.id is not None
            assert allotment.allotted_rank == 1500
            assert allotment.status == AllotmentStatus.ALLOTTED


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
