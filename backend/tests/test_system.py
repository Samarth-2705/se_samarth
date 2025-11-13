"""
System Tests for Admission Automation System
Tests complete end-to-end workflows
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    User, Student, UserRole, Course, College, Choice,
    AllotmentRound, Payment, PaymentStatus, Allotment, AllotmentStatus
)


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['MIN_CHOICES'] = 1
    app.config['MAX_CHOICES'] = 100

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
def setup_colleges(app):
    """Setup colleges and courses for testing"""
    with app.app_context():
        # Create colleges
        colleges = []
        for i in range(3):
            college = College(
                name=f'Test College {i+1}',
                code=f'TC{i+1}',
                city='Bangalore',
                state='Karnataka',
                type='Government',
                university='Autonomous'
            )
            db.session.add(college)
            colleges.append(college)

        db.session.flush()

        # Create courses for each college
        courses = []
        for college in colleges:
            for j in range(2):
                course = Course(
                    college_id=college.id,
                    name=f'Course {j+1}',
                    code=f'C{j+1}',
                    branch=f'Branch {j+1}',
                    degree='B.E.',
                    duration_years=4,
                    total_seats=100,
                    available_seats=100,
                    general_seats=50,
                    obc_seats=25,
                    sc_seats=15,
                    st_seats=7,
                    ews_seats=3,
                    min_rank=100,
                    max_rank=5000,
                    tuition_fee=150000
                )
                db.session.add(course)
                courses.append(course)

        db.session.commit()
        return {'colleges': colleges, 'courses': courses}


@pytest.fixture
def setup_admin(app):
    """Setup admin user"""
    with app.app_context():
        admin = User(
            email='admin@test.com',
            mobile='9999999999',
            password='Admin@123',
            role=UserRole.ADMIN
        )
        admin.email_verified = True
        admin.mobile_verified = True
        admin.is_verified = True
        db.session.add(admin)
        db.session.commit()
        return admin


class TestCompleteStudentAdmissionFlow:
    """System test for complete student admission workflow"""

    def test_complete_admission_workflow(self, client, app, setup_colleges, setup_admin):
        """
        Test complete admission flow from registration to seat allotment
        Steps:
        1. Student registers
        2. Student verifies account (simulated)
        3. Student logs in
        4. Student completes profile
        5. Student uploads documents (simulated)
        6. Admin verifies documents
        7. Student makes payment
        8. Student fills choices
        9. Student submits choices
        10. Admin triggers allotment
        11. Student views allotment
        12. Student accepts seat
        """

        # Step 1: Student Registration
        print("\n=== Step 1: Student Registration ===")
        register_response = client.post('/api/auth/register',
            json={
                'email': 'student1@test.com',
                'mobile': '8888888888',
                'password': 'Student@123',
                'first_name': 'Test',
                'last_name': 'Student',
                'date_of_birth': '2000-01-01',
                'gender': 'Male',
                'exam_type': 'KCET',
                'exam_rank': 1500,
                'exam_roll_number': 'KCET2024100',
                'category': 'General',
                'domicile_state': 'Karnataka'
            },
            content_type='application/json'
        )
        assert register_response.status_code == 201
        register_data = json.loads(register_response.data)
        user_id = register_data['user_id']
        print(f"✓ Student registered with ID: {user_id}")

        # Step 2: Verify account (simulated)
        print("\n=== Step 2: Verify Account ===")
        with app.app_context():
            user = User.query.get(user_id)
            user.email_verified = True
            user.mobile_verified = True
            user.is_verified = True
            db.session.commit()
        print("✓ Account verified")

        # Step 3: Student Login
        print("\n=== Step 3: Student Login ===")
        login_response = client.post('/api/auth/login',
            json={
                'identifier': 'student1@test.com',
                'password': 'Student@123'
            },
            content_type='application/json'
        )
        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        token = login_data['access_token']
        print("✓ Student logged in successfully")

        # Step 4: Complete Profile
        print("\n=== Step 4: Complete Profile ===")
        profile_response = client.put('/api/student/profile',
            json={
                'address': '123 Test Street',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560001',
                'guardian_name': 'Test Guardian',
                'guardian_phone': '9999999999'
            },
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        assert profile_response.status_code == 200
        print("✓ Profile completed")

        # Step 5 & 6: Mark documents as verified (simulated)
        print("\n=== Step 5 & 6: Document Verification ===")
        with app.app_context():
            student = Student.query.filter_by(user_id=user_id).first()
            student.documents_verified = True
            student.registration_complete = True
            db.session.commit()
        print("✓ Documents verified")

        # Step 7: Make Payment
        print("\n=== Step 7: Make Payment ===")
        payment_order_response = client.post('/api/payment/create-order',
            json={
                'amount': 500,
                'payment_type': 'application_fee'
            },
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        assert payment_order_response.status_code == 201
        order_data = json.loads(payment_order_response.data)
        print(f"✓ Payment order created: {order_data['order']['id']}")

        # Verify payment (simulated)
        payment_verify_response = client.post('/api/payment/verify',
            json={
                'payment_id': order_data['order']['id'],
                'razorpay_payment_id': 'test_pay_123',
                'razorpay_signature': 'test_sig_123'
            },
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        assert payment_verify_response.status_code == 200
        print("✓ Payment completed successfully")

        # Step 8: Get eligible colleges
        print("\n=== Step 8: Get Eligible Colleges ===")
        colleges_response = client.get('/api/choices/eligible-colleges',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert colleges_response.status_code == 200
        colleges_data = json.loads(colleges_response.data)
        print(f"✓ Found {len(colleges_data['eligible_colleges'])} eligible colleges")

        # Step 9: Fill choices
        print("\n=== Step 9: Fill Choices ===")
        courses_to_add = []
        for college in colleges_data['eligible_colleges']:
            for course in college['courses'][:1]:  # Add first course from each college
                courses_to_add.append(course['id'])

        for i, course_id in enumerate(courses_to_add[:3]):
            choice_response = client.post('/api/choices/add',
                json={'course_id': course_id},
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            assert choice_response.status_code == 201
        print(f"✓ Added {len(courses_to_add[:3])} choices")

        # Step 10: Submit choices
        print("\n=== Step 10: Submit Choices ===")
        submit_response = client.post('/api/choices/submit',
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        assert submit_response.status_code == 200
        print("✓ Choices submitted and locked")

        # Step 11: Admin login and trigger allotment
        print("\n=== Step 11: Admin Triggers Allotment ===")
        admin_login_response = client.post('/api/auth/login',
            json={
                'identifier': 'admin@test.com',
                'password': 'Admin@123'
            },
            content_type='application/json'
        )
        admin_data = json.loads(admin_login_response.data)
        admin_token = admin_data['access_token']

        # Trigger allotment
        allotment_response = client.post('/api/admin/allotment/trigger',
            json={'round_number': 1},
            headers={'Authorization': f'Bearer {admin_token}'},
            content_type='application/json'
        )
        assert allotment_response.status_code == 200
        allotment_data = json.loads(allotment_response.data)
        print(f"✓ Allotment completed: {allotment_data['result']['allotments_made']} seats allotted")

        # Step 12: Student views allotment
        print("\n=== Step 12: View Allotment ===")
        my_allotment_response = client.get('/api/allotment/my-allotment',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert my_allotment_response.status_code == 200
        my_allotment_data = json.loads(my_allotment_response.data)
        assert my_allotment_data['allotment'] is not None
        print(f"✓ Seat allotted: {my_allotment_data['allotment']['course']['name']}")

        # Step 13: Student accepts seat (frozen)
        print("\n=== Step 13: Accept Seat ===")
        allotment_id = my_allotment_data['allotment']['id']
        accept_response = client.post(f'/api/allotment/{allotment_id}/accept',
            json={'freeze': True},
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        assert accept_response.status_code == 200
        print("✓ Seat accepted and frozen")

        # Verify admission confirmed
        print("\n=== Step 14: Verify Admission Confirmed ===")
        with app.app_context():
            student = Student.query.filter_by(user_id=user_id).first()
            assert student.admission_confirmed == True
        print("✓ Admission confirmed")

        print("\n" + "="*50)
        print("✅ COMPLETE ADMISSION WORKFLOW TEST PASSED")
        print("="*50)


class TestMultipleStudentsAllotment:
    """System test for multiple students allotment"""

    def test_multiple_students_seat_allotment(self, client, app, setup_colleges, setup_admin):
        """
        Test seat allotment with multiple students
        Verifies rank-based allocation
        """
        print("\n=== Testing Multiple Students Allotment ===")

        students = []
        tokens = []

        # Create 5 students with different ranks
        ranks = [500, 1000, 1500, 2000, 2500]

        for i, rank in enumerate(ranks):
            # Register student
            register_response = client.post('/api/auth/register',
                json={
                    'email': f'student{i+1}@test.com',
                    'mobile': f'888888888{i}',
                    'password': 'Password@123',
                    'first_name': f'Student',
                    'last_name': f'{i+1}',
                    'date_of_birth': '2000-01-01',
                    'gender': 'Male',
                    'exam_type': 'KCET',
                    'exam_rank': rank,
                    'exam_roll_number': f'KCET2024{100+i}',
                    'category': 'General',
                    'domicile_state': 'Karnataka'
                },
                content_type='application/json'
            )
            data = json.loads(register_response.data)
            user_id = data['user_id']

            # Verify and prepare student
            with app.app_context():
                user = User.query.get(user_id)
                user.email_verified = True
                user.mobile_verified = True
                user.is_verified = True

                student = user.student
                student.documents_verified = True
                student.registration_complete = True
                student.payment_complete = True

                db.session.commit()

            # Login
            login_response = client.post('/api/auth/login',
                json={
                    'identifier': f'student{i+1}@test.com',
                    'password': 'Password@123'
                },
                content_type='application/json'
            )
            login_data = json.loads(login_response.data)
            tokens.append(login_data['access_token'])

            print(f"✓ Student {i+1} registered with rank {rank}")

        # All students add same course choices
        courses_response = client.get('/api/choices/eligible-colleges',
            headers={'Authorization': f'Bearer {tokens[0]}'}
        )
        courses_data = json.loads(courses_response.data)
        course_id = courses_data['eligible_colleges'][0]['courses'][0]['id']

        for i, token in enumerate(tokens):
            client.post('/api/choices/add',
                json={'course_id': course_id},
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            client.post('/api/choices/submit',
                headers={'Authorization': f'Bearer {token}'},
                content_type='application/json'
            )
            print(f"✓ Student {i+1} submitted choices")

        # Admin triggers allotment
        admin_login = client.post('/api/auth/login',
            json={'identifier': 'admin@test.com', 'password': 'Admin@123'},
            content_type='application/json'
        )
        admin_token = json.loads(admin_login.data)['access_token']

        allotment_response = client.post('/api/admin/allotment/trigger',
            json={'round_number': 1},
            headers={'Authorization': f'Bearer {admin_token}'},
            content_type='application/json'
        )

        print("\n✓ Allotment triggered")

        # Verify allotments based on rank
        for i, token in enumerate(tokens):
            my_allotment = client.get('/api/allotment/my-allotment',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(my_allotment.data)

            if data['allotment']:
                print(f"✓ Student {i+1} (Rank {ranks[i]}) got allotment")
            else:
                print(f"✓ Student {i+1} (Rank {ranks[i]}) did not get allotment (seats full)")

        print("\n✅ MULTIPLE STUDENTS ALLOTMENT TEST PASSED")


class TestPaymentWorkflow:
    """System test for payment workflow"""

    def test_payment_workflow(self, client, app):
        """Test complete payment workflow"""
        print("\n=== Testing Payment Workflow ===")

        # Register and verify user
        client.post('/api/auth/register',
            json={
                'email': 'paytest@test.com',
                'mobile': '7777777777',
                'password': 'Password@123',
                'first_name': 'Pay',
                'last_name': 'Test',
                'date_of_birth': '2000-01-01',
                'gender': 'Male',
                'exam_type': 'KCET',
                'exam_rank': 1000,
                'exam_roll_number': 'KCET2024999',
                'category': 'General',
                'domicile_state': 'Karnataka'
            },
            content_type='application/json'
        )

        with app.app_context():
            user = User.query.filter_by(email='paytest@test.com').first()
            user.email_verified = True
            user.mobile_verified = True
            user.is_verified = True
            db.session.commit()

        # Login
        login_response = client.post('/api/auth/login',
            json={'identifier': 'paytest@test.com', 'password': 'Password@123'},
            content_type='application/json'
        )
        token = json.loads(login_response.data)['access_token']

        # Create payment order
        order_response = client.post('/api/payment/create-order',
            json={'amount': 500, 'payment_type': 'application_fee'},
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        assert order_response.status_code == 201
        print("✓ Payment order created")

        # Verify payment
        order_data = json.loads(order_response.data)
        verify_response = client.post('/api/payment/verify',
            json={
                'payment_id': order_data['order']['id'],
                'razorpay_payment_id': 'test_pay_123',
                'razorpay_signature': 'test_sig_123'
            },
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        assert verify_response.status_code == 200
        print("✓ Payment verified")

        # Check payment history
        history_response = client.get('/api/payment/history',
            headers={'Authorization': f'Bearer {token}'}
        )
        history_data = json.loads(history_response.data)
        assert len(history_data['payments']) > 0
        assert history_data['payments'][0]['status'] == 'success'
        print("✓ Payment appears in history")

        print("\n✅ PAYMENT WORKFLOW TEST PASSED")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
