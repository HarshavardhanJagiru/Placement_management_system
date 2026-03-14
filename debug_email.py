import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Common configuration
SENDER_EMAIL = "reply.not.for.this.mail@gmail.com"
SENDER_PASSWORD = "vmlu ctyy gajk hlar"
receiver_email = "harshavardhanjagiru0218@gmail.com"

def test_mail():
    print(f"Attempting to send test email to {receiver_email}...")
    message = MIMEMultipart()
    message['From'] = f"Diagnostic Test <{SENDER_EMAIL}>"
    message['To'] = receiver_email
    message['Subject'] = "Placement Tracker Diagnostic"
    
    html_body = "<h1>Diagnostic Test</h1><p>If you see this, the SMTP configuration is working.</p>"
    message.attach(MIMEText(html_body, 'html'))
    
    try:
        print("Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("Logging in...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("Sending message...")
        server.send_message(message)
        print("SUCCESS: Email sent!")
        server.quit()
        return True
    except Exception as e:
        print(f"FAIL: {str(e)}")
        return False

if __name__ == "__main__":
    test_mail()
