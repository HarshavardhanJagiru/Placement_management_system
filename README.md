# University Placement Management System 🎓

A modern, full-stack Applicant Tracking System (ATS) and Placement Portal built with Flask and MySQL. This system bridging the gap between university placement cells and students by automating the recruitment workflow.

## 🌟 Key Features

### For Administrators (Placement Cell)
- **Advanced Dashboard**: Real-time analytics on placement metrics, department-wise tracking, and top recruiters using Chart.js.
- **Job Management**: Create, edit, and manage job postings with specified criteria (CGPA, deadline).
- **Automated Workflow (Kanban)**: Drag-and-drop application tracking (Applied -> Interview -> Offered -> Rejected).
- **Bulk Action Center**: Filter students dynamically by department and CGPA, and send customized bulk emails.
- **Automated Notifications**: System automatically dispatches emails for OTP verification, interview alerts, and background 24-hour reminders.
- **Export Reports**: Generate and download CSV reports of all student data for official records.

### For Students
- **Smart Profile**: Track CGPA, Department, Skills, and upload Resumes securely.
- **ATS Resume Parsing**: Automated data extraction from uploaded resumes.
- **Job Discovery**: View active drives and apply natively on the platform.
- **Personal Analytics**: Visual breakdown (Doughnut Chart) of individual application success rates.
- **Notification Inbox**: Read, manage, and delete real-time application updates.
- **Security Check**: Enforced password strength with frontend & backend validation, plus OTP-based password resets.

## 💻 Tech Stack
- **Backend Framework**: Python (Flask)
- **Database**: MySQL (`pymysql`)
- **Frontend Architecture**: HTML5, Vanilla CSS (`landing.css`, `style.css`), Bootstrap 5
- **Visualizations**: Chart.js
- **Background Tasks**: Python Threading
- **Authentication**: JWT/Session-based, SMTP Email Verification

## 🚀 Quick Setup Guide

### 1. Prerequisites
- Python 3.8+
- MySQL Server running locally

### 2. Environment Setup
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Initialization
Ensure your MySQL server is running. Then, run the initialization script to automatically create the schema and tables:
```bash
python init_db.py
```
*(Optionally) Insert sample data:*
```bash
python seed_data.py
```

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

## 🔐 Default Admin Credentials (If Seeded)
- **Email**: `admin@university.edu`
- **Password**: `AdminPassword!23` 

*(Or register a new account on the UI and manually set `role = 'admin'` in the database for the first time setup).*
