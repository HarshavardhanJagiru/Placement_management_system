import os
import requests
from datetime import datetime

# API KEY (set this in Render ENV)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")


def log_email_event(message):
    with open("email_log.txt", "a") as f:
        f.write(f"{datetime.now()}: {message}\n")


def _send_html_email(receiver_email, subject, html_body):
    """Send email using Resend API"""

    log_email_event(f"Attempting mail to {receiver_email} | Subject: {subject}")

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Placement Tracker <onboarding@resend.dev>",
                "to": [receiver_email],
                "subject": subject,
                "html": html_body
            }
        )

        print("RESEND RESPONSE:", response.status_code, response.text)

        if response.status_code == 200:
            log_email_event(f"SUCCESS: Mail sent to {receiver_email}")
            return True
        else:
            log_email_event(f"FAIL: {response.text}")
            return False

    except Exception as e:
        error_msg = f"Failed to send email: {e}"
        print(error_msg)
        log_email_event(error_msg)
        return False


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
