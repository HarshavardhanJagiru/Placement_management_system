from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, send_from_directory, jsonify
import pymysql
import random
import csv
import os
import io
import threading
import time
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from utils import send_otp_email, send_interview_alert, send_interview_reminder, send_reset_otp_email

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this for production

# Upload configuration
UPLOAD_FOLDER = 'static/uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database configuration
import os

db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME"),
    'port': int(os.getenv("DB_PORT", 3306)),
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
                if user:
                    if not user['is_verified']:
                        session['pending_user_id'] = user['id']
                        flash('Please verify your email address before logging in.', 'warning')
                        return redirect(url_for('verify_email'))

                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    session['username'] = user['username']
                    flash('Login successful!', 'success')
                    if user['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    return redirect(url_for('student_dashboard'))
                else:
                    flash('Invalid username or password', 'error')
        finally:
            db.close()
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        department = request.form['department']
        cgpa = request.form['cgpa']
        
        db = get_db_connection()
        try:
            with db.cursor() as cursor:
                # Generate 6 digit OTP
                otp_code = f"{random.randint(100000, 999999)}"
                otp_expiry = datetime.now() + timedelta(minutes=15)

                cursor.execute("INSERT INTO users (username, email, password, role, is_verified, otp_code, otp_expiry) VALUES (%s, %s, %s, 'student', FALSE, %s, %s)", 
                             (username, email, password, otp_code, otp_expiry))
                user_id = cursor.lastrowid
                
                cursor.execute("INSERT INTO students (user_id, full_name, department, cgpa) VALUES (%s, %s, %s, %s)", 
                             (user_id, full_name, department, cgpa))
                db.commit()
                
                # Send the OTP via Email
                print(f"DEBUG: Attempting to send OTP email to {email}...")
                success = send_otp_email(email, otp_code)
                if success:
                    print(f"DEBUG: OTP email sent successfully to {email}.")
                else:
                    print(f"ERROR: Failed to send OTP email to {email}.")
                
                # Setup session for verification
                session['pending_user_id'] = user_id
                flash('Registration almost complete! We sent a 6-digit code to your email.', 'info')
                return redirect(url_for('verify_email'))
        except Exception as e:
            db.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db_connection()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if user:
                    otp_code = f"{random.randint(100000, 999999)}"
                    otp_expiry = datetime.now() + timedelta(minutes=15)
                    cursor.execute("UPDATE users SET otp_code = %s, otp_expiry = %s WHERE id = %s", 
                                 (otp_code, otp_expiry, user['id']))
                    db.commit()
                    
                    if send_reset_otp_email(email, otp_code):
                        session['reset_email'] = email
                        flash('Password reset code sent to your email.', 'info')
                        return redirect(url_for('reset_password'))
                    else:
                        flash('Failed to send reset email. Please try again.', 'error')
                else:
                    flash('No account found with that email address.', 'error')
        except Exception as e:
            db.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            db.close()
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        submitted_otp = request.form['otp_code']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        email = session['reset_email']
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('reset_password'))

        db = get_db_connection()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT otp_code, otp_expiry FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and user['otp_code'] == submitted_otp:
                    if datetime.now() <= user['otp_expiry']:
                        cursor.execute("UPDATE users SET password = %s, otp_code = NULL, otp_expiry = NULL WHERE email = %s", 
                                     (new_password, email))
                        db.commit()
                        session.pop('reset_email', None)
                        flash('Password reset successful! You can now login.', 'success')
                        return redirect(url_for('login'))
                    else:
                        flash('Reset code has expired.', 'error')
                else:
                    flash('Invalid reset code.', 'error')
        except Exception as e:
            db.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            db.close()
            
    return render_template('reset_password.html')

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if 'pending_user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        submitted_otp = request.form['otp_code']
        user_id = session['pending_user_id']
        
        db = get_db_connection()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT otp_code, otp_expiry FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                
                if user and user['otp_code'] == submitted_otp:
                    if datetime.now() <= user['otp_expiry']:
                        # Valid OTP! Activate the user
                        cursor.execute("UPDATE users SET is_verified = TRUE, otp_code = NULL, otp_expiry = NULL WHERE id = %s", (user_id,))
                        
                        # Automatically log them in
                        cursor.execute("SELECT username, role FROM users WHERE id = %s", (user_id,))
                        active_user = cursor.fetchone()
                        
                        session['user_id'] = user_id
                        session['username'] = active_user['username']
                        session['role'] = active_user['role']
                        
                        session.pop('pending_user_id', None)
                        db.commit()
                        
                        flash('Email verified successfully! Welcome to your dashboard.', 'success')
                        return redirect(url_for('student_dashboard'))
                    else:
                        flash('Your verification code has expired. Please register again.', 'error')
                else:
                    flash('Invalid verification code. Please try again.', 'error')
        except Exception as e:
            db.rollback()
            flash(f'Error validating OTP: {str(e)}', 'error')
        finally:
            db.close()
            
    return render_template('verify_email.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            jobs = cursor.fetchall()
            # Get user's student record + CGPA
            cursor.execute("SELECT * FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            cursor.execute("SELECT job_id, status FROM applications WHERE student_id = %s", (student['id'],))
            applied_jobs = {app['job_id']: app['status'] for app in cursor.fetchall()}
            
            # Application stats for chart
            cursor.execute("SELECT status, COUNT(*) as count FROM applications WHERE student_id = %s GROUP BY status", (student['id'],))
            stats = cursor.fetchall()
            stats_dict = {row['status']: row['count'] for row in stats}
            
        return render_template('student_dashboard.html', jobs=jobs, applied_jobs=applied_jobs, student=student, stats_dict=stats_dict)
    finally:
        db.close()

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            jobs = cursor.fetchall()
            
            # Application list for management
            cursor.execute("""
                SELECT a.id, a.status, a.interview_date, j.position, j.company_name, 
                       s.full_name, s.skills as student_skills, j.required_skills as job_skills,
                       s.resume_filename, a.date_applied AS applied_at
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                JOIN students s ON a.student_id = s.id
                ORDER BY a.date_applied DESC
            """)
            raw_applications = cursor.fetchall()

            # Calculate match scores
            applications = []
            for app_data in raw_applications:
                score = 0
                if app_data['student_skills'] and app_data['job_skills']:
                    s_skills = set(s.strip().lower() for s in app_data['student_skills'].split(',') if s.strip())
                    j_skills = set(s.strip().lower() for s in app_data['job_skills'].split(',') if s.strip())
                    if j_skills:
                        intersection = s_skills.intersection(j_skills)
                        score = int((len(intersection) / len(j_skills)) * 100)
                
                app_data['match_score'] = score
                applications.append(app_data)

            # Stats for Chart.js
            cursor.execute("SELECT status, COUNT(*) as count FROM applications GROUP BY status")
            stats = cursor.fetchall()
            stats_dict = {row['status']: row['count'] for row in stats}

            cursor.execute("SELECT COUNT(*) as count FROM students")
            student_count = cursor.fetchone()['count']

            # Stats for charts
            cursor.execute("SELECT department, COUNT(*) as count FROM students WHERE department IS NOT NULL GROUP BY department")
            dept_stats = cursor.fetchall()
            
            cursor.execute("SELECT company_name, COUNT(*) as count FROM jobs GROUP BY company_name ORDER BY count DESC LIMIT 5")
            company_stats = cursor.fetchall()

            # Get list of all students for management
            cursor.execute("""
                SELECT s.full_name, u.username, u.email, s.department, s.cgpa, u.id as user_id
                FROM users u
                LEFT JOIN students s ON u.id = s.user_id
                WHERE u.role = 'student'
                ORDER BY u.username ASC
            """)
            students_list = cursor.fetchall()
            
        return render_template('admin_dashboard.html', 
                               jobs=jobs, 
                               applications=applications, 
                               stats_dict=stats_dict, 
                               student_count=student_count, 
                               students=students_list,
                               dept_stats=dept_stats,
                               company_stats=company_stats)
    finally:
        db.close()

@app.route('/admin/api/interviews')
def api_interviews():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT s.full_name, j.company_name, j.position, a.interview_date, a.id 
                FROM applications a
                JOIN students s ON a.student_id = s.id
                JOIN jobs j ON a.job_id = j.id
                WHERE a.status = 'interview' AND a.interview_date IS NOT NULL
            """)
            interviews = cursor.fetchall()
            
            events = []
            for inv in interviews:
                events.append({
                    'title': f"{inv['full_name']} - {inv['company_name']}",
                    'start': inv['interview_date'].isoformat() if inv['interview_date'] else None,
                    'color': '#20c997' # Bootstrap teal
                })
            return jsonify(events)
    finally:
        db.close()

@app.route('/admin/bulk-actions')
def admin_bulk_actions():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # Get departments for filter (from students table)
            cursor.execute("SELECT DISTINCT department FROM students WHERE department IS NOT NULL")
            departments = [row['department'] for row in cursor.fetchall()]
            
            # Get all students initially
            cursor.execute("""
                SELECT u.id, u.username, u.email, s.full_name, s.department, s.cgpa 
                FROM users u
                LEFT JOIN students s ON u.id = s.user_id
                WHERE u.role = 'student'
            """)
            students = cursor.fetchall()
            
    finally:
        db.close()
        
    return render_template('admin_bulk_actions.html', 
                           departments=departments, 
                           students=students)

@app.route('/admin/filter-students', methods=['POST'])
def filter_students():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    dept = data.get('department')
    min_cgpa = data.get('min_cgpa')
    
    query = """
        SELECT u.id, s.full_name, u.username, u.email, s.department, s.cgpa 
        FROM users u
        LEFT JOIN students s ON u.id = s.user_id
        WHERE u.role = 'student'
    """
    params = []
    
    if dept and dept != 'all':
        query += " AND s.department = %s"
        params.append(dept)
    
    if min_cgpa:
        query += " AND s.cgpa >= %s"
        params.append(float(min_cgpa))
        
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute(query, tuple(params))
            students = cursor.fetchall()
            # Convert values for JSON safety (especially Decimal/None)
            for s in students:
                if s['cgpa']: s['cgpa'] = float(s['cgpa'])
                if not s['full_name']: s['full_name'] = s['username']
    finally:
        db.close()
        
    return jsonify(students)

@app.route('/admin/send-bulk-message', methods=['POST'])
def send_bulk_message():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('login'))
        
    student_ids = request.form.getlist('student_ids')
    subject = request.form.get('subject')
    body = request.form.get('body')
    
    if not student_ids:
        flash('No students selected.', 'warning')
        return redirect(url_for('admin_bulk_actions'))
        
    db = get_db_connection()
    success_count = 0
    try:
        from utils import send_custom_email
        with db.cursor() as cursor:
            # Get emails for selected IDs
            format_strings = ','.join(['%s'] * len(student_ids))
            cursor.execute(f"SELECT email, username FROM users WHERE id IN ({format_strings})", tuple(student_ids))
            recipients = cursor.fetchall()
            
            for recipient in recipients:
                if send_custom_email(recipient['email'], subject, body):
                    success_count += 1
                    
    finally:
        db.close()
        
    flash(f'Successfully sent messages to {success_count} students.', 'success')
    return redirect(url_for('admin_bulk_actions'))

@app.route('/admin/application/<int:app_id>/<string:status>')
def update_status(app_id, status):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE applications SET status = %s WHERE id = %s", (status, app_id))
            
            # Auto-create notification for the student
            cursor.execute("""
                SELECT s.user_id, j.company_name, j.position 
                FROM applications a 
                JOIN students s ON a.student_id = s.id 
                JOIN jobs j ON a.job_id = j.id 
                WHERE a.id = %s
            """, (app_id,))
            app_info = cursor.fetchone()
            if app_info:
                status_labels = {'offered': '🎉 Congratulations! You received an Offer', 'rejected': '❌ Unfortunately, your application was Rejected', 'interview': '📅 You have been scheduled for an Interview'}
                msg = f"{status_labels.get(status, status.title())} for {app_info['position']} at {app_info['company_name']}."
                cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (app_info['user_id'], msg))
            
            db.commit()
            flash(f'Application {status}!', 'success')
    finally:
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/schedule_interview/<int:app_id>', methods=['POST'])
def schedule_interview(app_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    interview_date = request.form['interview_date']
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE applications SET status = 'interview', interview_date = %s WHERE id = %s", (interview_date, app_id))
            
            # Auto-create notification
            cursor.execute("""
                SELECT s.user_id, j.company_name, j.position, s.full_name, u.email
                FROM applications a 
                JOIN students s ON a.student_id = s.id 
                JOIN users u ON s.user_id = u.id
                JOIN jobs j ON a.job_id = j.id 
                WHERE a.id = %s
            """, (app_id,))
            app_info = cursor.fetchone()
            if app_info:
                msg = f"📅 Interview Scheduled for {app_info['position']} at {app_info['company_name']} on {interview_date}."
                cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (app_info['user_id'], msg))
                
                # Send Email Alert
                print(f"DEBUG: Triggering interview alert email to {app_info['email']}...")
                send_interview_alert(
                    app_info['email'], 
                    app_info['full_name'], 
                    app_info['company_name'], 
                    app_info['position'], 
                    interview_date
                )
                print("DEBUG: Interview alert triggered.")
            
            db.commit()
            flash('Interview successfully scheduled!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export_csv')
def export_csv():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT u.username, u.email, s.full_name, s.department, s.cgpa, s.skills, s.resume_filename
                FROM students s
                JOIN users u ON s.user_id = u.id
            """)
            students = cursor.fetchall()

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['Full Name', 'Username', 'Email', 'Department', 'CGPA', 'Skills', 'Resume Filename'])
            
            # Rows
            for student in students:
                writer.writerow([
                    student['full_name'], 
                    student['username'], 
                    student['email'], 
                    student['department'], 
                    student['cgpa'], 
                    student['skills'], 
                    student['resume_filename'] if student['resume_filename'] else 'No Resume'
                ])
            
            output.seek(0)
            
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-disposition": "attachment; filename=placement_report.csv"}
            )
    finally:
        db.close()

@app.route('/student/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            if request.method == 'POST':
                full_name = request.form['full_name']
                department = request.form['department']
                cgpa = request.form['cgpa']
                skills = request.form['skills']
                
                # Handle resume upload
                resume_filename = None
                if 'resume_file' in request.files:
                    file = request.files['resume_file']
                    if file and file.filename != '':
                        if allowed_file(file.filename):
                            filename = secure_filename(f"resume_{session['user_id']}_{file.filename}")
                            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                                os.makedirs(app.config['UPLOAD_FOLDER'])
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            resume_filename = filename
                        else:
                            flash('Invalid file type. Only PDF and DOCX are allowed.', 'error')

                if resume_filename:
                    cursor.execute("""
                        UPDATE students 
                        SET full_name=%s, department=%s, cgpa=%s, skills=%s, resume_filename=%s 
                        WHERE user_id=%s
                    """, (full_name, department, cgpa, skills, resume_filename, session['user_id']))
                else:
                    cursor.execute("""
                        UPDATE students 
                        SET full_name=%s, department=%s, cgpa=%s, skills=%s 
                        WHERE user_id=%s
                    """, (full_name, department, cgpa, skills, session['user_id']))
                
                db.commit()
                flash('Profile updated successfully!', 'success')
            
            cursor.execute("SELECT * FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
        return render_template('profile.html', student=student)
    finally:
        db.close()

@app.route('/student/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # First, find the student_id if it exists
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
            student = cursor.fetchone()
            
            if student:
                student_id = student['id']
                # 1. Delete applications
                cursor.execute("DELETE FROM applications WHERE student_id = %s", (student_id,))
                
            # 2. Delete notifications
            cursor.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
            
            # 3. Delete student profile
            cursor.execute("DELETE FROM students WHERE user_id = %s", (user_id,))
            
            # 4. Finally delete user
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            
            db.commit()
            session.clear()
            flash('Your account has been permanently deleted.', 'info')
            return redirect(url_for('index'))
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Deletion error: {str(e)}")
        flash(f'Error deleting account: {str(e)}', 'error')
        return redirect(url_for('profile'))
    finally:
        db.close()

@app.route('/admin/delete_student/<int:user_id>', methods=['POST'])
def admin_delete_student(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # First, find the student_id if it exists
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
            student = cursor.fetchone()
            
            if student:
                student_id = student['id']
                # 1. Delete applications
                cursor.execute("DELETE FROM applications WHERE student_id = %s", (student_id,))
                
            # 2. Delete notifications
            cursor.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
            
            # 3. Delete student profile
            cursor.execute("DELETE FROM students WHERE user_id = %s", (user_id,))
            
            # 4. Finally delete user
            cursor.execute("DELETE FROM users WHERE id = %s AND role = 'student'", (user_id,))
            
            db.commit()
            flash('Student account deleted successfully.', 'success')
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Admin deletion error: {str(e)}")
        flash(f'Error deleting student: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    user_id = session['user_id']
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if user and user['password'] == current_password:
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
                db.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Incorrect current password.', 'error')
    except Exception as e:
        db.rollback()
        flash(f'Error updating password: {str(e)}', 'error')
    finally:
        db.close()
    
    return redirect(request.referrer or url_for('index'))

@app.route('/view_resume/<path:filename>')
def view_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/student/api/interviews')
def student_api_interviews():
    if 'user_id' not in session or session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # First get student_id
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            if not student:
                return jsonify([])
                
            cursor.execute("""
                SELECT j.company_name, j.position, a.interview_date 
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE a.student_id = %s AND a.status = 'interview' AND a.interview_date IS NOT NULL
            """, (student['id'],))
            interviews = cursor.fetchall()
            
            events = []
            for inv in interviews:
                events.append({
                    'title': f"Interview: {inv['company_name']} ({inv['position']})",
                    'start': inv['interview_date'].isoformat() if inv['interview_date'] else None,
                    'color': '#20c997' # Bootstrap teal
                })
            return jsonify(events)
    finally:
        db.close()

@app.route('/student/my_applications')
def my_applications():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            cursor.execute("""
                SELECT a.id, a.status, a.date_applied AS applied_at, a.interview_date, j.position, j.company_name, j.description, j.salary 
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE a.student_id = %s
                ORDER BY a.date_applied DESC
            """, (student['id'],))
            apps = cursor.fetchall()
        return render_template('my_applications.html', applications=apps)
    finally:
        db.close()

@app.route('/admin/add_job', methods=['POST'])
def add_job():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    company_name = request.form['company_name']
    position = request.form['position']
    salary = request.form['salary']
    deadline = request.form['deadline']
    description = request.form['description']
    required_skills = request.form['required_skills']
    min_cgpa = request.form.get('min_cgpa', 0.0)
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO jobs (company_name, position, salary, deadline, description, required_skills, min_cgpa) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                         (company_name, position, salary, deadline, description, required_skills, min_cgpa))
            db.commit()
            flash('Job posted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_job/<int:job_id>', methods=['POST'])
def edit_job(job_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    company_name = request.form['company_name']
    position = request.form['position']
    salary = request.form['salary']
    deadline = request.form['deadline']
    description = request.form['description']
    required_skills = request.form['required_skills']
    min_cgpa = request.form.get('min_cgpa', 0.0)
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""UPDATE jobs SET company_name=%s, position=%s, salary=%s, deadline=%s, 
                           description=%s, required_skills=%s, min_cgpa=%s WHERE id=%s""",
                         (company_name, position, salary, deadline, description, required_skills, min_cgpa, job_id))
            db.commit()
            flash('Job updated successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
            db.commit()
            flash('Job deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/student/apply/<int:job_id>', methods=['POST'])
def apply(job_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # Get student info including CGPA
            cursor.execute("SELECT id, cgpa FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            
            # Check CGPA eligibility
            cursor.execute("SELECT min_cgpa FROM jobs WHERE id = %s", (job_id,))
            job = cursor.fetchone()
            if job and job['min_cgpa'] and student['cgpa'] and float(student['cgpa']) < float(job['min_cgpa']):
                flash(f'You are not eligible for this job. Minimum CGPA required: {job["min_cgpa"]}. Your CGPA: {student["cgpa"]}.', 'error')
                return redirect(url_for('student_dashboard'))
            
            # Check if already applied
            cursor.execute("SELECT * FROM applications WHERE job_id = %s AND student_id = %s", (job_id, student['id']))
            existing = cursor.fetchone()
            if existing:
                if existing['status'] == 'saved':
                    cursor.execute("UPDATE applications SET status='applied', date_applied=CURRENT_TIMESTAMP WHERE id=%s", (existing['id'],))
                    db.commit()
                    flash('Application submitted successfully!', 'success')
                else:
                    flash('You have already applied for this job.', 'warning')
            else:
                cursor.execute("INSERT INTO applications (job_id, student_id, status) VALUES (%s, %s, 'applied')", (job_id, student['id']))
                db.commit()
                flash('Application submitted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('student_dashboard'))

@app.route('/student/save_job/<int:job_id>', methods=['POST'])
def save_job(job_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            
            cursor.execute("SELECT * FROM applications WHERE job_id = %s AND student_id = %s", (job_id, student['id']))
            if cursor.fetchone():
                flash('Job is already tracked in your applications.', 'warning')
            else:
                cursor.execute("INSERT INTO applications (job_id, student_id, status) VALUES (%s, %s, 'saved')", (job_id, student['id']))
                db.commit()
                flash('Job saved to Need to Apply!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('student_dashboard'))

@app.route('/student/update_status_ajax', methods=['POST'])
def update_status_ajax():
    if 'user_id' not in session or session['role'] != 'student':
        return {'success': False, 'message': 'Unauthorized'}, 401
        
    app_id = request.form.get('app_id')
    new_status = request.form.get('new_status')
    
    valid_statuses = ['saved', 'applied', 'in_progress', 'interview', 'offered', 'rejected']
    if new_status not in valid_statuses:
        return {'success': False, 'message': 'Invalid status'}, 400
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # Verify the student actually owns this application
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            
            # LOCK: Prevent students from dragging admin-finalized cards
            cursor.execute("SELECT status FROM applications WHERE id = %s AND student_id = %s", (app_id, student['id']))
            current = cursor.fetchone()
            if current and current['status'] in ('offered', 'rejected'):
                return {'success': False, 'message': 'This application has been finalized by the admin and cannot be moved.'}, 403
            
            cursor.execute("UPDATE applications SET status = %s WHERE id = %s AND student_id = %s", (new_status, app_id, student['id']))
            db.commit()
            return {'success': True}
    except Exception as e:
        db.rollback()
        return {'success': False, 'message': str(e)}, 500
    finally:
        db.close()

@app.route('/student/notifications')
def student_notifications():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
            notifications = cursor.fetchall()
            
            # Mark all as read
            cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE", (session['user_id'],))
            db.commit()
        return render_template('notifications.html', notifications=notifications)
    finally:
        db.close()

@app.route('/student/notifications/clear', methods=['POST'])
def clear_notifications():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
        
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM notifications WHERE user_id = %s", (session['user_id'],))
            db.commit()
            flash('All notifications have been cleared.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        db.close()
        
    return redirect(url_for('student_notifications'))

@app.route('/student/notifications/delete/<int:notif_id>', methods=['POST'])
def delete_notification(notif_id):
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
        
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM notifications WHERE id = %s AND user_id = %s", (notif_id, session['user_id']))
            db.commit()
            flash('Notification deleted.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
    finally:
        db.close()
        
    return redirect(url_for('student_notifications'))

@app.context_processor
def inject_notification_count():
    if 'user_id' in session and session.get('role') == 'student':
        db = get_db_connection()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE", (session['user_id'],))
                unread = cursor.fetchone()['count']
            return {'unread_count': unread}
        finally:
            db.close()
    return {'unread_count': 0}

def background_reminder_task():
    """Background task to send interview reminders 24h before"""
    while True:
        try:
            db = get_db_connection()
            with db.cursor() as cursor:
                # Find interviews in next 24 hours that haven't had a reminder sent
                # and where status is 'interview'
                now = datetime.now()
                tomorrow = now + timedelta(hours=24)
                
                cursor.execute("""
                    SELECT a.id, a.interview_date, j.company_name, j.position, s.full_name, u.email
                    FROM applications a
                    JOIN jobs j ON a.job_id = j.id
                    JOIN students s ON a.student_id = s.id
                    JOIN users u ON s.user_id = u.id
                    WHERE a.status = 'interview' 
                    AND a.reminder_sent = FALSE
                    AND a.interview_date <= %s
                    AND a.interview_date > %s
                """, (tomorrow, now))
                
                upcoming = cursor.fetchall()
                for app_data in upcoming:
                    print(f"Sending reminder to {app_data['email']} for interview at {app_data['company_name']}")
                    success = send_interview_reminder(
                        app_data['email'],
                        app_data['full_name'],
                        app_data['company_name'],
                        app_data['position'],
                        app_data['interview_date'].strftime('%Y-%m-%d %H:%M') if isinstance(app_data['interview_date'], datetime) else str(app_data['interview_date'])
                    )
                    if success:
                        cursor.execute("UPDATE applications SET reminder_sent = TRUE WHERE id = %s", (app_data['id'],))
                        db.commit()
                        
            db.close()
        except Exception as e:
            print(f"Error in background reminder task: {e}")
            if 'db' in locals():
                db.close()
        
        # Check every hour
        time.sleep(3600)

if __name__ == '__main__':
    app.run(debug=True)
