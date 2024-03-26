import base64
import hashlib
from datetime import datetime, timedelta
import random
import string
import smtplib, ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Auth:
    def __init__(self) -> None:
        pass

    def generate_user_id(self, username: str) -> str:
        # Get current time
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
         
        # Combine username and current time
        user_id = f"{username}_{current_time}"
        
        # Encode user_id to bytes and then Base64
        user_id = base64.b64encode(user_id.encode()).decode()
        
        return user_id

    def encrypt_password(self, password: str, user_id: str) -> str:
        # Combine user_id and password
        combined_string = f"{user_id}/{password}"

        # Hash the combined string using SHA-256
        hashed_password = hashlib.sha256(combined_string.encode()).digest()

        # Base64 encode the hashed password
        encoded_password = base64.b64encode(hashed_password)

        return encoded_password.decode()

    def compare_passwords(self, user_id, entered_password, stored_password):
        # Hash the entered password using the same method as the stored password
        hashed_entered_password = self.encrypt_password(entered_password, user_id)

        # Compare the hashed entered password with the stored password
        return hashed_entered_password == stored_password

    # Simple OTP generation function
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))

    # Email sending function
    def send_email(self, email, otp):
        sender_email = os.environ.get("OTP_EMAIL")
        receiver_email = email
        password = os.environ.get("OTP_EMAIL_PASS")

        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "[MHD] Password Reset OTP"

        text = f"Your OTP for password reset is: {otp}"

        message.attach(MIMEText(text, "plain"))
        gmail_host = os.environ.get("GMAIL_HOST")
        gmail_port = os.environ.get("GMAIL_PORT")
        context = ssl.create_default_context()
        with smtplib.SMTP(gmail_host, gmail_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    

