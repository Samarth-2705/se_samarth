# Admission Automation System for Professional Courses

A comprehensive web-based platform to automate the admission process for competitive exams like KCET and COMEDK. This system streamlines student registration, document verification, choice filling, seat allotment, fee payment, and admission confirmation processes.

## 📋 Table of Contents

- [Project Information](#project-information)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [User Roles](#user-roles)
- [Security Features](#security-features)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 📌 Project Information

**Project Name:** Admission Automation System for Professional Courses
**Version:** 1.0.0
**Team:** SE MINI
**Institution:** PES University
**Course:** UE23CS341A
**Academic Year:** 2025
**Semester:** 5th Sem

### Team Members
- [@Sami9692](https://github.com/Sami9692) - Scrum Master
- [@SamhithRGowda](https://github.com/SamhithRGowda) - Developer
- [@Sahil-0788](https://github.com/Sahil-0788) - Developer
- [@Samarth-2705](https://github.com/Samarth-2705) - Developer

## ✨ Features

### Student Features
- ✅ User Registration with OTP Verification (Email & SMS)
- ✅ Secure Login with JWT Authentication
- ✅ Profile Management
- ✅ Document Upload and Management
- ✅ Application Fee Payment via Razorpay
- ✅ College/Course Choice Filling
- ✅ View Seat Allotment Results
- ✅ Accept/Reject Allotted Seats
- ✅ Download Receipts and Allotment Letters
- ✅ Real-time Notifications (Email & SMS)

### Administrator Features
- ✅ Dashboard with Comprehensive Statistics
- ✅ Student Application Management
- ✅ Document Verification System
- ✅ Merit List Generation
- ✅ Automated Seat Allotment Algorithm
- ✅ Multiple Rounds of Seat Allotment
- ✅ Payment and Refund Management
- ✅ Report Generation (PDF/CSV)
- ✅ Audit Logging

### Security Features
- ✅ Multi-Factor Authentication (MFA) for Admins
- ✅ Role-Based Access Control (RBAC)
- ✅ TLS 1.2+ Encryption for Data in Transit
- ✅ AES-256 Encryption for Data at Rest
- ✅ Session Management with Auto-Logout
- ✅ Account Lockout after Failed Login Attempts
- ✅ Password Strength Requirements
- ✅ PCI-DSS Compliant Payment Processing

## 🛠️ Technology Stack

### Backend
- **Framework:** Flask 3.0.0 (Python)
- **Database:** MySQL / PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (Flask-JWT-Extended)
- **Password Hashing:** Bcrypt
- **Email:** Flask-Mail
- **SMS:** Twilio
- **Payment Gateway:** Razorpay
- **Task Queue:** Celery + Redis
- **Caching:** Redis
- **File Upload:** Werkzeug

### Frontend
- **Framework:** React 18.2.0
- **Routing:** React Router DOM v6
- **HTTP Client:** Axios
- **Form Handling:** Formik + Yup
- **Notifications:** React-Toastify
- **State Management:** React Context API

### Infrastructure
- **Hosting:** AWS / Azure (Cloud)
- **Load Balancer:** AWS ELB / Azure Load Balancer
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **CI/CD:** GitHub Actions

## 📁 Project Structure

```
admission-automation-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── config/
│   │   │   └── config.py            # Configuration settings
│   │   ├── models/                  # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User and authentication
│   │   │   ├── student.py           # Student profile
│   │   │   ├── document.py          # Document management
│   │   │   ├── college.py           # College and courses
│   │   │   ├── choice.py            # Student preferences
│   │   │   ├── allotment.py         # Seat allotment
│   │   │   ├── payment.py           # Payments
│   │   │   ├── notification.py      # Notifications
│   │   │   ├── otp.py               # OTP management
│   │   │   └── audit_log.py         # Audit logging
│   │   ├── routes/                  # API endpoints
│   │   │   ├── auth.py              # Authentication routes
│   │   │   ├── student.py           # Student routes
│   │   │   ├── admin.py             # Admin routes
│   │   │   ├── document.py          # Document routes
│   │   │   ├── payment.py           # Payment routes
│   │   │   ├── choice.py            # Choice filling routes
│   │   │   └── allotment.py         # Allotment routes
│   │   ├── services/                # Business logic
│   │   │   ├── email_service.py     # Email notifications
│   │   │   ├── sms_service.py       # SMS notifications
│   │   │   ├── payment_service.py   # Payment processing
│   │   │   └── seat_allotment_service.py  # Allotment algorithm
│   │   └── utils/                   # Utility functions
│   │       ├── encryption.py        # Data encryption
│   │       └── validators.py        # Input validation
│   ├── tests/                       # Backend tests
│   ├── requirements.txt             # Python dependencies
│   ├── run.py                       # Application entry point
│   └── .env.example                 # Environment variables template
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/              # Reusable components
│   │   ├── pages/                   # Page components
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── StudentDashboard.js
│   │   │   ├── AdminDashboard.js
│   │   │   ├── Profile.js
│   │   │   ├── Documents.js
│   │   │   ├── ChoiceFilling.js
│   │   │   ├── SeatAllotment.js
│   │   │   ├── Payment.js
│   │   │   └── styles.css
│   │   ├── services/
│   │   │   └── api.js               # API service layer
│   │   ├── utils/
│   │   │   └── AuthContext.js       # Authentication context
│   │   ├── App.js                   # Main app component
│   │   └── index.js                 # Entry point
│   ├── package.json                 # Node dependencies
│   └── .env                         # Environment variables
├── docs/                            # Documentation
│   ├── SRS_SE.docx                  # Software Requirements Specification
│   └── SAD_Admission_Automation_System_7Deliverables.docx  # Architecture Document
├── scripts/                         # Deployment and utility scripts
├── .gitignore
└── README.md                        # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 16+
- MySQL 8.0+ or PostgreSQL 13+
- Redis 6.0+
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/pestechnology/PESU_EC_CSE_H_P01_Automation_for_admission_to_professional_courses_SE-MINI.git
cd PESU_EC_CSE_H_P01_Automation_for_admission_to_professional_courses_SE-MINI/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Key environment variables:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Email configuration
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`: SMS configuration
- `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`: Payment gateway

5. **Initialize database**
```bash
flask db init
flask db migrate
flask db upgrade

# Seed sample data
flask seed_db
```

6. **Run the application**
```bash
python run.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env
```

4. **Run the application**
```bash
npm start
```

Frontend will be available at `http://localhost:3000`

### Running with Docker (Optional)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Backend: http://localhost:5000
# Frontend: http://localhost:3000
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "student@example.com",
  "mobile": "9876543210",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "2005-01-15",
  "gender": "Male",
  "exam_type": "KCET",
  "exam_rank": 1234,
  "exam_roll_number": "KCET2024-12345",
  "category": "General"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "identifier": "student@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

#### Verify OTP
```http
POST /auth/verify-otp
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "user_id": 1,
  "otp": "123456",
  "type": "email"  // or "mobile"
}
```

### Student Endpoints

#### Get Profile
```http
GET /student/profile
Authorization: Bearer {access_token}
```

#### Update Profile
```http
PUT /student/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "address_line1": "123 Main Street",
  "city": "Bangalore",
  "state": "Karnataka",
  "pincode": "560001"
}
```

#### Get Dashboard
```http
GET /student/dashboard
Authorization: Bearer {access_token}
```

### Document Endpoints

#### Upload Document
```http
POST /documents/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [binary]
document_type: "marks_card_10th"
```

#### List Documents
```http
GET /documents/list
Authorization: Bearer {access_token}
```

### Payment Endpoints

#### Create Payment Order
```http
POST /payment/create-order
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "amount": 1000,
  "payment_type": "application_fee"
}
```

#### Verify Payment
```http
POST /payment/verify
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "payment_id": 1,
  "razorpay_payment_id": "pay_XXXXX",
  "razorpay_signature": "signature_XXXXX"
}
```

### Choice Filling Endpoints

#### Get Eligible Colleges
```http
GET /choices/eligible-colleges
Authorization: Bearer {access_token}
```

#### Add Choice
```http
POST /choices/add
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "course_id": 1
}
```

#### Submit Choices
```http
POST /choices/submit
Authorization: Bearer {access_token}
```

### Allotment Endpoints

#### Get My Allotment
```http
GET /allotment/my-allotment
Authorization: Bearer {access_token}
```

#### Accept Seat
```http
POST /allotment/{id}/accept
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "freeze": true  // true = freeze, false = accept with upgrade
}
```

### Admin Endpoints

#### Get Dashboard
```http
GET /admin/dashboard
Authorization: Bearer {access_token}
```

#### Trigger Seat Allotment
```http
POST /admin/allotment/trigger
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "round_number": 1
}
```

## 👥 User Roles

### Student
- Register and create profile
- Upload documents
- Make payments
- Fill college preferences
- View and accept seat allotment

### Administrator
- Verify documents
- Generate merit lists
- Trigger seat allotment
- Manage refunds
- Generate reports
- View system statistics

### College Official
- View allotted students
- Verify and confirm admissions

## 🔒 Security Features

1. **Authentication & Authorization**
   - JWT-based authentication
   - Role-Based Access Control (RBAC)
   - Multi-Factor Authentication for admins
   - Session management with auto-logout

2. **Data Security**
   - TLS 1.2+ encryption for data in transit
   - AES-256 encryption for sensitive data at rest
   - Secure password storage with Bcrypt
   - No storage of credit card information

3. **Account Security**
   - Password strength requirements
   - Account lockout after failed attempts
   - IP-based rate limiting
   - Audit logging of all actions

4. **Payment Security**
   - PCI-DSS compliant payment gateway
   - Secure payment processing via Razorpay
   - Transaction verification
   - Refund management

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 🚢 Deployment

### Production Checklist

1. **Environment Configuration**
   - Set `FLASK_ENV=production`
   - Update `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure production database
   - Set up Redis for caching
   - Configure email and SMS services
   - Set up payment gateway credentials

2. **Database**
   - Run migrations
   - Set up database backups
   - Configure connection pooling

3. **Security**
   - Enable HTTPS/TLS
   - Configure firewall rules
   - Set up rate limiting
   - Enable audit logging

4. **Monitoring**
   - Set up Prometheus + Grafana
   - Configure ELK stack for logging
   - Set up alerts for critical events

5. **Deployment Steps**
```bash
# Build frontend
cd frontend
npm run build

# Deploy to AWS/Azure
# Configure load balancer
# Set up auto-scaling
# Configure CDN for frontend assets
```

## 📄 License

This project is developed for educational purposes as part of the PES University UE23CS341A curriculum.

## 🤝 Contributing

This is an academic project. For any queries or suggestions, please contact the development team.

## 📞 Support

For issues or questions:
- Create an issue in the GitHub repository
- Contact: Teaching Assistants at PES University

---

**Developed with ❤️ by Team SE MINI**
**PES University | UE23CS341A | 2025**
