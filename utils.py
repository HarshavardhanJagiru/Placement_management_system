import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_otp_email(receiver_email, otp_code):
    sender_email = "reply.not.for.this.mail@gmail.com"
    sender_password = "vmlu ctyy gajk hlar"  # User provided App Password
    
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = f"Placement Tracker <{sender_email}>"
    message['To'] = receiver_email
    message['Subject'] = "Your Placement Tracker Verification Code"
    
    # Beautiful HTML body
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
          <h2 style="color: #4f46e5; text-align: center; margin-bottom: 20px;">Welcome to Placement Tracker!</h2>
          <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">Thank you for registering. Please use the following One-Time Password (OTP) to verify your stunning new dashboard account.</p>
          <div style="text-align: center; margin: 30px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1e293b; background: #e2e8f0; padding: 10px 20px; border-radius: 8px;">{otp_code}</span>
          </div>
          <p style="color: #718096; font-size: 14px; text-align: center;">This code will expire in exactly 15 minutes.</p>
          <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
          <p style="color: #a0aec0; font-size: 12px; text-align: center;">If you didn't request this email, please ignore it.</p>
        </div>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, 'html'))
    
    # Create SMTP session
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Enable security
        server.login(sender_email, sender_password) # Login
        server.send_message(message)
        print(f"OTP email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    finally:
        server.quit()
