import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Common configuration
SENDER_EMAIL = "reply.not.for.this.mail@gmail.com"
SENDER_PASSWORD = "vmlu ctyy gajk hlar"  # User provided App Password

def log_email_event(message):
    with open("email_log.txt", "a") as f:
        f.write(f"{datetime.now()}: {message}\n")

def _send_html_email(receiver_email, subject, html_body):
    """Internal helper to send HTML emails"""
    log_email_event(f"Attempting mail to {receiver_email} | Subject: {subject}")
    message = MIMEMultipart()
    message['From'] = f"Placement Tracker <{SENDER_EMAIL}>"
    message['To'] = receiver_email
    message['Subject'] = subject
    
    message.attach(MIMEText(html_body, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
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

def send_otp_email(receiver_email, otp_code):
    subject = "Your Placement Tracker Verification Code"
    html_body = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
          <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #4f46e5; margin: 0; font-size: 24px;">Welcome to Placement Tracker!</h2>
          </div>
          <p style="color: #475569; font-size: 16px; line-height: 1.6;">Thank you for registering. Please use the following One-Time Password (OTP) to verify your stunning new dashboard account.</p>
          <div style="text-align: center; margin: 35px 0;">
            <span style="font-size: 36px; font-weight: bold; letter-spacing: 6px; color: #1e293b; background: #f1f5f9; padding: 15px 30px; border-radius: 12px; border: 1px solid #e2e8f0;">{otp_code}</span>
          </div>
          <p style="color: #64748b; font-size: 14px; text-align: center;">This code will expire in exactly 15 minutes.</p>
          <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 30px 0;">
          <p style="color: #94a3b8; font-size: 12px; text-align: center;">If you didn't request this email, please ignore it.</p>
        </div>
      </body>
    </html>
    """
    return _send_html_email(receiver_email, subject, html_body)

def send_interview_alert(receiver_email, student_name, company, position, date_time):
    subject = f"Interview Scheduled: {position} at {company}"
    html_body = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-top: 4px solid #4f46e5;">
          <h2 style="color: #1e293b; margin-top: 0;">Hi {student_name}, 🎉</h2>
          <p style="color: #475569; font-size: 16px; line-height: 1.6;">Great news! An interview has been scheduled for your application.</p>
          <div style="background: #f8fafc; padding: 25px; border-radius: 12px; margin: 30px 0; border: 1px solid #e2e8f0;">
            <table style="width: 100%; border-collapse: collapse;">
              <tr><td style="color: #64748b; padding-bottom: 10px;">Company:</td><td style="color: #1e293b; font-weight: bold; padding-bottom: 10px;">{company}</td></tr>
              <tr><td style="color: #64748b; padding-bottom: 10px;">Position:</td><td style="color: #1e293b; font-weight: bold; padding-bottom: 10px;">{position}</td></tr>
              <tr><td style="color: #64748b;">Schedule:</td><td style="color: #4f46e5; font-weight: bold;">{date_time}</td></tr>
            </table>
          </div>
          <p style="color: #475569; font-size: 16px;">Please be prepared and log in to your dashboard for more details.</p>
          <div style="text-align: center; margin-top: 30px;">
            <a href="#" style="background: #4f46e5; color: white; padding: 12px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; display: inline-block;">Go to Dashboard</a>
          </div>
        </div>
      </body>
    </html>
    """
    return _send_html_email(receiver_email, subject, html_body)

def send_interview_reminder(receiver_email, student_name, company, position, date_time):
    subject = f"Friendly Reminder: Interview at {company} tomorrow"
    html_body = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #fffbeb; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-top: 4px solid #f59e0b;">
          <h2 style="color: #1e293b; margin-top: 0;">Hi {student_name}, 👋</h2>
          <p style="color: #475569; font-size: 16px; line-height: 1.6;">This is a friendly reminder for your upcoming interview tomorrow.</p>
          <div style="background: #fffbeb; padding: 25px; border-radius: 12px; margin: 30px 0; border: 1px solid #fef3c7;">
            <table style="width: 100%; border-collapse: collapse;">
              <tr><td style="color: #92400e; padding-bottom: 10px;">Company:</td><td style="color: #1e293b; font-weight: bold; padding-bottom: 10px;">{company}</td></tr>
              <tr><td style="color: #92400e; padding-bottom: 10px;">Position:</td><td style="color: #1e293b; font-weight: bold; padding-bottom: 10px;">{position}</td></tr>
              <tr><td style="color: #92400e;">When:</td><td style="color: #b45309; font-weight: bold;">{date_time}</td></tr>
            </table>
          </div>
          <p style="color: #475569; font-size: 16px;">Good luck! We believe in you.</p>
        </div>
      </body>
    </html>
    """
    return _send_html_email(receiver_email, subject, html_body)

def send_reset_otp_email(receiver_email, otp_code):
    subject = "Password Reset Verification Code"
    html_body = f"""
    <html>
      <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-top: 4px solid #ef4444;">
          <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ef4444; margin: 0; font-size: 24px;">Password Reset Request</h2>
          </div>
          <p style="color: #475569; font-size: 16px; line-height: 1.6;">We received a request to reset your password. Please use the following One-Time Password (OTP) to proceed with the reset.</p>
          <div style="text-align: center; margin: 35px 0;">
            <span style="font-size: 36px; font-weight: bold; letter-spacing: 6px; color: #1e293b; background: #f1f5f9; padding: 15px 30px; border-radius: 12px; border: 1px solid #e2e8f0;">{otp_code}</span>
          </div>
          <p style="color: #64748b; font-size: 14px; text-align: center;">This code will expire in exactly 15 minutes.</p>
          <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 30px 0;">
          <p style="color: #94a3b8; font-size: 12px; text-align: center;">If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
        </div>
      </body>
    </html>
    """
    return _send_html_email(receiver_email, subject, html_body)
