
from twilio.rest import Client
import os

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'your-account-sid')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'your-auth-token')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')
        
    def send_booking_sms(self, customer_phone, customer_name, package_type):
        try:
            client = Client(self.account_sid, self.auth_token)
            
            message = client.messages.create(
                body=f"Dear {customer_name}, your {package_type} booking with S-E-C Agency is confirmed! We'll contact you soon with details.",
                from_=self.from_number,
                to=customer_phone
            )
            
            return True
        except Exception as e:
            print(f"SMS error: {e}")
            return False
