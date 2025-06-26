
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv('EMAIL_USER', 'your-email@gmail.com')
        self.password = os.getenv('EMAIL_PASSWORD', 'your-app-password')
    
    def send_booking_confirmation(self, customer_email, customer_name, package_type, amount):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = customer_email
            msg['Subject'] = "Booking Confirmation - S-E-C Agency"
            
            body = f"""
            Dear {customer_name},
            
            Thank you for booking with S-E-C Agency!
            
            Booking Details:
            - Package: {package_type}
            - Amount: ${amount}
            - Status: Confirmed
            
            We will contact you soon with further details about your pilgrimage journey.
            
            Best regards,
            S-E-C Agency Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, customer_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
