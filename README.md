# Employee Info & Certificate Verification Portal

A secure and responsive system for employees to view their data and upload certificates for verification.

## Features

### Admin Module
- Admin Login
- View/Add/Edit Employee Information
- View & Verify Certificates
- View Task Records

### Employee Module
- Enter ID to access Profile
- View Task History
- Upload Certificates
- View Certificate Verification Status

## Technology Stack
- Frontend: HTML, CSS
- Backend: Python (Django)
- Database: MySQL

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure database settings in settings.py

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Database Schema

### employees
- emp_id (Primary Key)
- name
- designation
- join_date
- profile_image

### tasks
- task_id (Primary Key)
- emp_id (Foreign Key)
- task_title
- task_detail
- task_date

### certificates
- cert_id (Primary Key)
- emp_id (Foreign Key)
- cert_title
- cert_file
- cert_status
- upload_date 