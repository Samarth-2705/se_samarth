# Testing Documentation

This directory contains comprehensive tests for the Admission Automation System.

## Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── test_unit.py          # Unit tests (individual components)
├── test_integration.py   # Integration tests (API endpoints)
├── test_system.py        # System tests (end-to-end workflows)
└── README.md            # This file
```

## Types of Tests

### 1. Unit Tests (`test_unit.py`)
Tests individual components in isolation:
- User model (creation, password hashing, verification)
- Student model (profile creation, full name, application status)
- College and Course models (creation, relationships)
- Choice model (creation, to_dict method)
- Payment model (creation, status updates)
- Allotment model (creation)

### 2. Integration Tests (`test_integration.py`)
Tests interaction between components and API endpoints:
- Authentication API (register, login, get current user)
- Student API (profile, dashboard)
- Choice Filling API (eligible colleges, add/list/submit choices)
- Payment API (create order, payment history)
- Admin API (dashboard, students list, trigger allotment)
- Allotment API (view allotment, rounds)

### 3. System Tests (`test_system.py`)
Tests complete end-to-end workflows:
- Complete student admission flow (registration to seat acceptance)
- Multiple students allotment (rank-based allocation)
- Payment workflow (order creation to verification)

## Prerequisites

Install testing dependencies:

```bash
pip install pytest pytest-cov
```

Or if you have a requirements file:

```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
# From backend directory
pytest

# With verbose output
pytest -v

# With output printed
pytest -v -s
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/test_unit.py -v

# Integration tests only
pytest tests/test_integration.py -v

# System tests only
pytest tests/test_system.py -v
```

### Run Specific Test Classes

```bash
# Test user model only
pytest tests/test_unit.py::TestUserModel -v

# Test authentication API only
pytest tests/test_integration.py::TestAuthenticationAPI -v

# Test complete admission workflow
pytest tests/test_system.py::TestCompleteStudentAdmissionFlow -v
```

### Run Specific Test Methods

```bash
# Test specific method
pytest tests/test_unit.py::TestUserModel::test_user_creation -v

# Test login functionality
pytest tests/test_integration.py::TestAuthenticationAPI::test_user_login_success -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View HTML coverage report
# Open htmlcov/index.html in your browser
```

### Run Tests Matching a Pattern

```bash
# Run all tests with "payment" in the name
pytest -k payment -v

# Run all tests with "student" in the name
pytest -k student -v
```

## Test Results Interpretation

### Successful Test Output
```
tests/test_unit.py::TestUserModel::test_user_creation PASSED        [10%]
tests/test_unit.py::TestUserModel::test_password_hashing PASSED     [20%]
...
========================= 50 passed in 5.23s ==========================
```

### Failed Test Output
```
tests/test_unit.py::TestUserModel::test_user_creation FAILED        [10%]

================================ FAILURES =================================
________________________ TestUserModel.test_user_creation ________________
    def test_user_creation(self, app):
        with app.app_context():
            user = User(...)
>           assert user.email == 'expected@test.com'
E           AssertionError: assert 'actual@test.com' == 'expected@test.com'
```

## Writing New Tests

### Unit Test Template

```python
class TestNewFeature:
    """Unit tests for new feature"""

    def test_feature_functionality(self, app):
        """Test feature works correctly"""
        with app.app_context():
            # Arrange
            # ... setup test data

            # Act
            # ... perform action

            # Assert
            assert result == expected
```

### Integration Test Template

```python
class TestNewAPI:
    """Integration tests for new API endpoint"""

    def test_api_endpoint(self, client, auth_token):
        """Test API endpoint responds correctly"""
        response = client.get('/api/new-endpoint',
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'expected_field' in data
```

### System Test Template

```python
class TestNewWorkflow:
    """System test for new workflow"""

    def test_complete_workflow(self, client, app):
        """Test complete workflow from start to finish"""
        # Step 1: Setup
        # ...

        # Step 2: Execute workflow
        # ...

        # Step 3: Verify results
        # ...
```

## Common Test Fixtures

### `app`
Creates a test application with in-memory SQLite database.

### `client`
Test client for making HTTP requests.

### `sample_user`
Creates a verified user for testing.

### `sample_student`
Creates a student profile linked to a user.

### `auth_token`
JWT authentication token for student user.

### `admin_token`
JWT authentication token for admin user.

## Debugging Tests

### Print Debug Information

```python
def test_something(self, app):
    with app.app_context():
        user = User.query.first()
        print(f"User: {user.email}")  # Will show in output with -s flag
        assert user is not None
```

### Run with Python Debugger

```bash
# Run with debugger
pytest --pdb

# Drop into debugger on failure
pytest --pdb -x
```

### Run Single Test with Output

```bash
pytest tests/test_unit.py::TestUserModel::test_user_creation -v -s
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Clear Names**: Use descriptive test method names that explain what is being tested
3. **AAA Pattern**: Arrange, Act, Assert - structure tests clearly
4. **Mock External Services**: Don't make real API calls or send real emails in tests
5. **Test Edge Cases**: Test both success and failure scenarios
6. **Keep Tests Fast**: Unit tests should run in milliseconds
7. **Use Fixtures**: Reuse common setup code with pytest fixtures
8. **Clean Up**: Tests should not leave data behind (use in-memory database)

## Continuous Integration

To run tests in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest -v --cov=app
```

## Troubleshooting

### Import Errors
Make sure you're in the backend directory and virtual environment is activated:
```bash
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Database Errors
Tests use in-memory SQLite database. If you see database errors, check:
- SQLAlchemy models are correct
- Relationships are properly defined
- Foreign keys are valid

### Authentication Errors
If authentication tests fail:
- Check JWT_SECRET_KEY is set
- Verify user is marked as verified
- Ensure password hashing is working

## Test Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: All API endpoints covered
- **System Tests**: All critical workflows covered

## Contact

For questions about testing, contact the development team or refer to pytest documentation:
https://docs.pytest.org/
