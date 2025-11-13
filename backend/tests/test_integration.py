"""
Integration Tests for Admission Automation System
Tests interaction between components and API endpoints
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Student, UserRole, Course, College, Choice, AllotmentRound, Payment, PaymentStatus


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

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
def verified_user(app):
    """Create a verified user"""
    with app.app_context():
        user = User(
            email='student@test.com',
            mobile='9876543210',
            password='Password123',
            role=UserRole.STUDENT
        )
        user.email_verified = True
        user.mobile_verified = True
        user.is_verified = True
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            first_name='Test',
            last_name='Student',
            date_of_birth=datetime(2000, 1, 1).date(),
            gender='Male',
            exam_type='KCET',
            exam_rank=1500,
            exam_roll_number='KCET2024001',
            category='General',
            domicile_state='Karnataka'
        )
        db.session.add(student)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(app):
    """Create an admin user"""
    with app.app_context():
        user = User(
            email='admin@test.com',
            mobile='9999999999',
            password='Admin123',
            role=UserRole.ADMIN
        )
        user.email_verified = True
        user.mobile_verified = True
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_token(client, verified_user):
    """Get authentication token for verified user"""
    response = client.post('/api/auth/login',
        json={
            'identifier': 'student@test.com',
            'password': 'Password123'
        },
        content_type='application/json'
    )
    data = json.loads(response.data)
    return data.get('access_token')


@pytest.fixture
def admin_token(client, admin_user):
    """Get authentication token for admin"""
    response = client.post('/api/auth/login',
        json={
            'identifier': 'admin@test.com',
            'password': 'Admin123'
        },
        content_type='application/json'
    )
    data = json.loads(response.data)
    return data.get('access_token')


@pytest.fixture
def sample_college_course(app):
    """Create sample college and course"""
    with app.app_context():
        college = College(
            name='Test Institute',
            code='TI',
            city='Bangalore',
            state='Karnataka',
            type='Government',
            university='Autonomous'
        )
        db.session.add(college)
        db.session.flush()

        course = Course(
            college_id=college.id,
            name='Computer Science',
            code='CSE',
            branch='Computer Science',
            degree='B.E.',
            duration_years=4,
            total_seats=100,
            available_seats=100,
            general_seats=50,
            min_rank=100,
            max_rank=5000,
            tuition_fee=150000
        )
        db.session.add(course)
        db.session.commit()
        return {'college': college, 'course': course}


class TestAuthenticationAPI:
    """Integration tests for authentication endpoints"""

    def test_user_registration(self, client):
        """Test user registration flow"""
        response = client.post('/api/auth/register',
            json={
                'email': 'newuser@test.com',
                'mobile': '8888888888',
                'password': 'Newpass123',
                'first_name': 'New',
                'last_name': 'User',
                'date_of_birth': '2000-01-01',
                'gender': 'Male',
                'exam_type': 'KCET',
                'exam_rank': 2000,
                'exam_roll_number': 'KCET2024002',
                'category': 'General',
                'domicile_state': 'Karnataka'
            },
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert data['email'] == 'newuser@test.com'

    def test_user_login_success(self, client, verified_user):
        """Test successful login"""
        response = client.post('/api/auth/login',
            json={
                'identifier': 'student@test.com',
                'password': 'Password123'
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'student@test.com'

    def test_user_login_failure(self, client, verified_user):
        """Test failed login with wrong password"""
        response = client.post('/api/auth/login',
            json={
                'identifier': 'student@test.com',
                'password': 'wrongpassword'
            },
            content_type='application/json'
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_current_user(self, client, auth_token):
        """Test getting current user details"""
        response = client.get('/api/auth/me',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == 'student@test.com'


class TestStudentAPI:
    """Integration tests for student endpoints"""

    def test_get_student_profile(self, client, auth_token):
        """Test getting student profile"""
        response = client.get('/api/student/profile',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'student' in data
        assert data['student']['first_name'] == 'Test'
        assert data['student']['exam_rank'] == 1500

    def test_update_student_profile(self, client, auth_token):
        """Test updating student profile"""
        response = client.put('/api/student/profile',
            json={
                'address': '123 Test Street',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560001'
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['student']['address'] == '123 Test Street'

    def test_get_student_dashboard(self, client, auth_token):
        """Test getting student dashboard"""
        response = client.get('/api/student/dashboard',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'profile' in data


class TestChoiceFillingAPI:
    """Integration tests for choice filling endpoints"""

    def test_get_eligible_colleges(self, client, auth_token, sample_college_course):
        """Test getting eligible colleges"""
        response = client.get('/api/choices/eligible-colleges',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'eligible_colleges' in data
        assert len(data['eligible_colleges']) > 0

    def test_add_choice(self, client, auth_token, sample_college_course):
        """Test adding a choice"""
        course_id = sample_college_course['course'].id

        response = client.post('/api/choices/add',
            json={'course_id': course_id},
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'choice' in data
        assert data['choice']['course_id'] == course_id

    def test_list_choices(self, client, auth_token, sample_college_course):
        """Test listing choices"""
        # Add a choice first
        course_id = sample_college_course['course'].id
        client.post('/api/choices/add',
            json={'course_id': course_id},
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        # List choices
        response = client.get('/api/choices/list',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'choices' in data
        assert len(data['choices']) == 1

    def test_submit_choices(self, client, auth_token, sample_college_course):
        """Test submitting choices"""
        # Add a choice first
        course_id = sample_college_course['course'].id
        client.post('/api/choices/add',
            json={'course_id': course_id},
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        # Submit choices
        response = client.post('/api/choices/submit',
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data


class TestPaymentAPI:
    """Integration tests for payment endpoints"""

    def test_create_payment_order(self, client, auth_token):
        """Test creating payment order"""
        response = client.post('/api/payment/create-order',
            json={
                'amount': 500,
                'payment_type': 'application_fee'
            },
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'order' in data
        assert data['order']['amount'] == 500

    def test_payment_history(self, client, auth_token):
        """Test getting payment history"""
        response = client.get('/api/payment/history',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'payments' in data


class TestAdminAPI:
    """Integration tests for admin endpoints"""

    def test_admin_dashboard(self, client, admin_token):
        """Test admin dashboard"""
        response = client.get('/api/admin/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'students' in data
        assert 'financial' in data

    def test_get_all_students(self, client, admin_token):
        """Test getting all students"""
        response = client.get('/api/admin/students',
            headers={'Authorization': f'Bearer {admin_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'students' in data
        assert 'pagination' in data

    def test_trigger_allotment(self, client, admin_token, app, sample_college_course):
        """Test triggering seat allotment"""
        with app.app_context():
            # Create allotment round first
            round = AllotmentRound(
                round_number=1,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                acceptance_deadline=datetime.utcnow() + timedelta(days=10)
            )
            db.session.add(round)
            db.session.commit()

        response = client.post('/api/admin/allotment/trigger',
            json={'round_number': 1},
            headers={'Authorization': f'Bearer {admin_token}'},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data


class TestAllotmentAPI:
    """Integration tests for allotment endpoints"""

    def test_get_my_allotment_no_seat(self, client, auth_token):
        """Test getting allotment when no seat allotted"""
        response = client.get('/api/allotment/my-allotment',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['allotment'] is None

    def test_get_allotment_rounds(self, client, auth_token, app):
        """Test getting allotment rounds"""
        with app.app_context():
            round = AllotmentRound(
                round_number=1,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                acceptance_deadline=datetime.utcnow() + timedelta(days=10)
            )
            db.session.add(round)
            db.session.commit()

        response = client.get('/api/allotment/rounds',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rounds' in data
        assert len(data['rounds']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
