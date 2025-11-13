"""
Validation utilities for input data
"""
import re
from datetime import datetime


def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_mobile(mobile):
    """Validate Indian mobile number"""
    if not mobile:
        return False
    # Remove any non-digit characters
    mobile = re.sub(r'\D', '', mobile)
    # Check if it's a valid Indian mobile number (10 digits starting with 6-9)
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, mobile))


def validate_password(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, "Password is valid"


def validate_pincode(pincode):
    """Validate Indian pincode"""
    if not pincode:
        return False
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, pincode))


def validate_date(date_str, date_format='%Y-%m-%d'):
    """Validate date format"""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except (ValueError, TypeError):
        return False


def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    if not filename:
        return False
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size, max_size):
    """Validate file size in bytes"""
    return file_size <= max_size


def sanitize_filename(filename):
    """Sanitize filename to prevent security issues"""
    # Remove any path components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove any non-alphanumeric characters except dots, hyphens, and underscores
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def validate_rank(rank):
    """Validate exam rank"""
    try:
        rank = int(rank)
        return 1 <= rank <= 1000000  # Assuming max rank is 1 million
    except (ValueError, TypeError):
        return False


def validate_exam_roll_number(roll_number):
    """Validate exam roll number format"""
    if not roll_number:
        return False
    # Allow alphanumeric characters and hyphens
    pattern = r'^[A-Z0-9-]{5,20}$'
    return bool(re.match(pattern, roll_number.upper()))
