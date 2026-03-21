import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")

if not SENDER_EMAIL or not SENDER_PASSWORD:
    print("ERROR: Email credentials not set in environment variables")


def log_email_event(message):
    with open("email_log.txt", "a") as f:
        f.write(f"{datetime.now()}: {message}\n")


def _send_html_email(receiver_email, subject, html_body):
    """Internal helper to send HTML emails"""

    print(f"DEBUG: Connecting to SMTP for {receiver_email}...")
    log_email_event(f"Attempting mail to {receiver_email} | Subject: {subject}")

    message = MIMEMultipart()
    message['From'] = f"Placement Tracker <{SENDER_EMAIL}>"
    message['To'] = receiver_email
    message['Subject'] = subject

    message.attach(MIMEText(html_body, 'html'))

    try:
        
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)

        print(f"SUCCESS: Email sent to {receiver_email}")
        log_email_event(f"SUCCESS: Mail sent to {receiver_email}")

        return True

    except Exception as e:
        error_msg = f"Failed to send email to {receiver_email}: {e}"
        print(error_msg)
        log_email_event(f"FAIL: {error_msg}")
        return False

    finally:
        if 'server' in locals():
            server.quit()


# ---------------- EMAIL FUNCTIONS ----------------

def send_otp_email(receiver_email, otp_code):
    subject = "Your Placement Tracker Verification Code"

    html_body = f"""
    <html>
      <body>
        <h2>Welcome to Placement Tracker!</h2>
        <p>Your OTP is:</p>
        <h1>{otp_code}</h1>
        <p>Expires in 15 minutes.</p>
      </body>
    </html>
    """

    return _send_html_email(receiver_email, subject, html_body)


def send_interview_alert(receiver_email, student_name, company, position, date_time):
    subject = f"Interview Scheduled: {position} at {company}"

    html_body = f"""
    <html>
      <body>
        <h2>Hi {student_name}</h2>
        <p>Your interview has been scheduled.</p>
        <p><b>Company:</b> {company}</p>
        <p><b>Position:</b> {position}</p>
        <p><b>Date:</b> {date_time}</p>
      </body>
    </html>
    """

    return _send_html_email(receiver_email, subject, html_body)


def send_interview_reminder(receiver_email, student_name, company, position, date_time):
    subject = f"Reminder: Interview at {company}"

    html_body = f"""
    <html>
      <body>
        <h2>Hi {student_name}</h2>
        <p>This is a reminder for your interview.</p>
        <p><b>Company:</b> {company}</p>
        <p><b>Position:</b> {position}</p>
        <p><b>Date:</b> {date_time}</p>
      </body>
    </html>
    """

    return _send_html_email(receiver_email, subject, html_body)


def send_reset_otp_email(receiver_email, otp_code):
    subject = "Password Reset OTP"

    html_body = f"""
    <html>
      <body>
        <h2>Password Reset</h2>
        <p>Your OTP is:</p>
        <h1>{otp_code}</h1>
      </body>
    </html>
    """

    return _send_html_email(receiver_email, subject, html_body)


def send_custom_email(receiver_email, subject, body_text):
    html_body = f"""
    <html>
      <body>
        <h2>Placement Update</h2>
        <p>{body_text}</p>
      </body>
    </html>
    """

    return _send_html_email(receiver_email, subject, html_body)
