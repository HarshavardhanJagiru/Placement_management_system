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
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# Upload config
UPLOAD_FOLDER = 'static/uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ DATABASE (ENV BASED)
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


# ✅ ASYNC EMAIL HELPERS
def send_interview_email_async(email, name, company, position, interview_date):
    try:
        send_interview_alert(email, name, company, position, interview_date)
    except Exception as e:
        print(f"Email error: {e}")

def send_bulk_email_async(recipients, subject, body):
    from utils import send_custom_email
    for recipient in recipients:
        try:
            send_custom_email(recipient['email'], subject, body)
        except Exception as e:
            print(f"Bulk email error: {e}")


# ---------------- ROUTES ----------------

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
                cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
                user = cursor.fetchone()

                if user:
                    session['user_id'] = user['id']
                    session['role'] = user['role']
                    return redirect(url_for('admin_dashboard' if user['role']=='admin' else 'student_dashboard'))
                else:
                    flash("Invalid credentials", "error")
        finally:
            db.close()

    return render_template('login.html')


# ---------------- DASHBOARDS ----------------

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs")
            jobs = cursor.fetchall()
        return render_template('student_dashboard.html', jobs=jobs)
    finally:
        db.close()


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs")
            jobs = cursor.fetchall()
        return render_template('admin_dashboard.html', jobs=jobs)
    finally:
        db.close()


# ---------------- BULK EMAIL ----------------

@app.route('/admin/send-bulk-message', methods=['POST'])
def send_bulk_message():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    student_ids = request.form.getlist('student_ids')
    subject = request.form.get('subject')
    body = request.form.get('body')

    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            format_strings = ','.join(['%s'] * len(student_ids))
            cursor.execute(f"SELECT email FROM users WHERE id IN ({format_strings})", tuple(student_ids))
            recipients = cursor.fetchall()

            # ✅ ASYNC CALL
            threading.Thread(
                target=send_bulk_email_async,
                args=(recipients, subject, body)
            ).start()

    finally:
        db.close()

    flash("Emails are being sent in background", "success")
    return redirect(url_for('admin_dashboard'))


# ---------------- SCHEDULE INTERVIEW ----------------

@app.route('/admin/schedule_interview/<int:app_id>', methods=['POST'])
def schedule_interview(app_id):
    interview_date = request.form['interview_date']

    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE applications SET interview_date=%s WHERE id=%s", (interview_date, app_id))

            cursor.execute("""
                SELECT u.email, s.full_name, j.company_name, j.position
                FROM applications a
                JOIN students s ON a.student_id=s.id
                JOIN users u ON s.user_id=u.id
                JOIN jobs j ON a.job_id=j.id
                WHERE a.id=%s
            """, (app_id,))
            app_info = cursor.fetchone()

            if app_info:
                # ✅ ASYNC EMAIL
                threading.Thread(
                    target=send_interview_email_async,
                    args=(
                        app_info['email'],
                        app_info['full_name'],
                        app_info['company_name'],
                        app_info['position'],
                        interview_date
                    )
                ).start()

        db.commit()
    finally:
        db.close()

    flash("Interview scheduled!", "success")
    return redirect(url_for('admin_dashboard'))


# ---------------- FILE SERVE ----------------

@app.route('/view_resume/<path:filename>')
def view_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---------------- ERROR ----------------

@app.errorhandler(404)
def not_found(e):
    return "404 Not Found", 404


# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)
