from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this for production

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'Harsha',
    'password': 'Harsha0218!',
    'database': 'placement_db',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**db_config)

@app.route('/')
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
                # Insert into users
                cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'student')", 
                             (username, email, password))
                user_id = cursor.lastrowid
                # Insert into students
                cursor.execute("INSERT INTO students (user_id, full_name, department, cgpa) VALUES (%s, %s, %s, %s)", 
                             (user_id, full_name, department, cgpa))
                db.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
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
    return redirect(url_for('login'))

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            jobs = cursor.fetchall()
            # Get user's applications
            cursor.execute("SELECT students.id FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            cursor.execute("SELECT job_id FROM applications WHERE student_id = %s", (student['id'],))
            applied_jobs = [app['job_id'] for app in cursor.fetchall()]
        return render_template('student_dashboard.html', jobs=jobs, applied_jobs=applied_jobs)
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
                SELECT a.id, a.status, a.interview_date, j.position, j.company_name, s.full_name, a.date_applied AS applied_at
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                JOIN students s ON a.student_id = s.id
                ORDER BY a.date_applied DESC
            """)
            applications = cursor.fetchall()

            # Stats for Chart.js
            cursor.execute("SELECT status, COUNT(*) as count FROM applications GROUP BY status")
            stats = cursor.fetchall()
            stats_dict = {row['status']: row['count'] for row in stats}

            cursor.execute("SELECT COUNT(*) as count FROM students")
            student_count = cursor.fetchone()['count']
            
        return render_template('admin_dashboard.html', jobs=jobs, applications=applications, stats_dict=stats_dict, student_count=student_count)
    finally:
        db.close()

@app.route('/admin/application/<int:app_id>/<string:status>')
def update_status(app_id, status):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE applications SET status = %s WHERE id = %s", (status, app_id))
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
            db.commit()
            flash('Interview successfully scheduled!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('admin_dashboard'))

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
                resume_url = request.form['resume_url']
                cursor.execute("""
                    UPDATE students SET full_name=%s, department=%s, cgpa=%s, resume_url=%s 
                    WHERE user_id=%s
                """, (full_name, department, cgpa, resume_url, session['user_id']))
                db.commit()
                flash('Profile updated!', 'success')
            
            cursor.execute("SELECT * FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
        return render_template('profile.html', student=student)
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
                SELECT a.status, a.date_applied AS applied_at, a.interview_date, j.position, j.company_name, j.description, j.salary 
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
    
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO jobs (company_name, position, salary, deadline, description) VALUES (%s, %s, %s, %s, %s)", 
                         (company_name, position, salary, deadline, description))
            db.commit()
            flash('Job posted successfully!', 'success')
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
            # Get student id
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            # Check if already applied
            cursor.execute("SELECT * FROM applications WHERE job_id = %s AND student_id = %s", (job_id, student['id']))
            if cursor.fetchone():
                flash('You have already applied for this job.', 'warning')
            else:
                cursor.execute("INSERT INTO applications (job_id, student_id) VALUES (%s, %s)", (job_id, student['id']))
                db.commit()
                flash('Application submitted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        db.close()
    return redirect(url_for('student_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
