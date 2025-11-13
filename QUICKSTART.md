# Quick Start Guide - Admission Automation System

This guide will help you get the Admission Automation System up and running quickly on your local machine.

## Prerequisites

Ensure you have the following installed:
- Python 3.9 or higher
- Node.js 16 or higher
- MySQL 8.0 or PostgreSQL 13
- Git

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd se_samarth
```

### 2. Backend Setup (5 minutes)

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file with your database credentials
# Minimum required:
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/admission_system
# SECRET_KEY=your-secret-key-here
# JWT_SECRET_KEY=your-jwt-secret-here
```

### 3. Initialize Database

```bash
# Initialize and create tables
flask init-db

# Seed sample data (colleges and courses)
flask seed-db
```

### 4. Start Backend Server

```bash
# Run the Flask application
python run.py

# Backend will be available at: http://localhost:5000
# API endpoints at: http://localhost:5000/api
```

Keep this terminal open!

### 5. Frontend Setup (3 minutes)

Open a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env

# Start React development server
npm start

# Frontend will be available at: http://localhost:3000
```

## Test the Application

### Create a Student Account

1. Open your browser and go to `http://localhost:3000`
2. Click on "Register"
3. Fill in the registration form with:
   - Personal details (name, DOB, gender)
   - Contact details (email, mobile)
   - Create a password (min 8 characters, must include uppercase, lowercase, number, special character)
   - Exam details (type, rank, roll number, category)
4. Click "Register"
5. **Note:** Without actual SMTP/SMS setup, OTP verification will fail. For testing, you can:
   - Check the backend console for the generated OTP codes
   - Or temporarily modify the verification logic

### Login and Explore

1. After registration, go to "Login"
2. Enter your email/mobile and password
3. Explore the student dashboard
4. Check out different features:
   - Profile management
   - Document upload
   - Payment simulation
   - Choice filling
   - Seat allotment

## Default Test Data

After running `flask seed-db`, the following test data is available:

### Colleges
- PES University (Code: COL001)
- RV College of Engineering (Code: COL002)

### Courses (at PES University)
- Computer Science and Engineering (CSE)
- Electronics and Communication Engineering (ECE)

### Course (at RV College)
- Computer Science and Engineering (CSE)

## Common Issues & Solutions

### Issue: Database Connection Error

**Solution:**
- Ensure MySQL/PostgreSQL is running
- Check DATABASE_URL in .env file
- Create the database if it doesn't exist:
  ```sql
  CREATE DATABASE admission_system;
  ```

### Issue: Port 5000 already in use

**Solution:**
Change the port in `backend/run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

Then update frontend .env:
```bash
REACT_APP_API_URL=http://localhost:5001/api
```

### Issue: Frontend not connecting to backend

**Solution:**
- Check if backend is running
- Verify REACT_APP_API_URL in frontend .env
- Check browser console for CORS errors
- Ensure CORS is properly configured in backend

### Issue: Module not found errors

**Solution:**
- Backend: Make sure you're in the virtual environment
- Frontend: Run `npm install` again
- Check Python/Node versions

## Optional: Email & SMS Setup

For full functionality, configure:

### Email (using Gmail):

1. Get an App Password from Google Account settings
2. Update .env:
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### SMS (using Twilio):

1. Sign up for Twilio trial account
2. Get credentials and update .env:
```bash
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

## Next Steps

1. **Explore the Admin Panel:**
   - Create an admin user manually in the database
   - Login and explore admin features

2. **Test the Workflow:**
   - Complete student registration
   - Upload documents
   - Fill college choices
   - Trigger seat allotment (as admin)
   - Accept allotted seat

3. **Customize:**
   - Add more colleges and courses
   - Modify UI styling
   - Add custom features

## Development Tips

### Backend Hot Reload
Flask runs in debug mode by default, so changes are auto-reloaded.

### Frontend Hot Reload
React automatically reloads on file changes.

### Database Changes
After modifying models:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### View API Documentation
- API endpoints: Check `backend/app/routes/`
- Test with Postman or curl
- Use the Swagger documentation (if configured)

## Getting Help

- Check the main README_PROJECT.md for detailed documentation
- Review the PRD for feature specifications
- Check logs in backend console for errors
- Use browser DevTools for frontend debugging

## Ready to Deploy?

See `DEPLOYMENT.md` for production deployment instructions.

---

**You're all set! Happy developing! 🚀**
