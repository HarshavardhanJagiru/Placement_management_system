# Placement Management System

A simple, functional full-stack application for managing student placements, job postings, and applications. Built as an individual FSD project using modern web technologies.

## 🚀 Features

- **Semantic HTML5**: Structured using header, nav, section, and footer tags.
- **Bootstrap UI**: Professional look and feel using cards, modals, and grid system.
- **jQuery Validation**: Real-time client-side form validation for a better user experience.
- **Flask Backend**: Robust routing and Jinja2 templating.
- **MySQL Database**: Persistent storage for students, jobs, and applications.

## 🛠️ Tech Stack

- **Frontend**: HTML5, Bootstrap 5, jQuery
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Dependencies**: cryptography, pymysql

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- MySQL Server (XAMPP/WAMP)

### 2. Installation
1. Clone or copy the project to your local machine.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Database Initialization
1. Ensure your MySQL server is running.
2. Update the `db_config` in `app.py` and `init_db.py` if your credentials differ.
3. Run the initialization script:
   ```bash
   python init_db.py
   python seed_data.py
   ```

### 4. Running the App
Start the Flask server:
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

## 📸 Demo Steps
1. **Register**: Sign up as a new student.
2. **Browse Jobs**: View available opportunities on the dashboard.
3. **Apply**: Submit an application for a job.
4. **Admin Panel**: Login as admin (`admin/admin123`) to post new jobs and view statistics.

## 📜 License
This project is for educational purposes.
