import base64
import hashlib
from datetime import datetime, timedelta
import random
import string
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from database import connector
from const import const

class Auth:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db

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
        hashed_entered_password = self.encrypt_password(user_id, entered_password)

        # Compare the hashed entered password with the stored password
        return hashed_entered_password == stored_password

    # Simple OTP generation function
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))

    # Email sending function
    def send_email(email, otp):
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
        with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    def exist_username(self, username: str) -> bool:
        user_data = self.db.execute_query("SELECT customer_id FROM tbl_customer WHERE username = %s", (username,))
        if len(user_data) > 0:
            return True
        return False

    def login(self, username: str, password: str) -> bool:
        # Retrieve user data from the database by email
        user_data = self.db.execute_query("SELECT customer_id, password FROM tbl_customer WHERE username = %s", (username,))
        
        if user_data:
            # Extract user_id and stored_password from the retrieved data
            customer_id, stored_password = user_data[0]

            # Compare the hashed entered password with the stored password
            return self.compare_passwords(customer_id, password, stored_password)
        else:
            return False
    
    def sign_up(self, username: str, password: str, full_name: str, email: str) -> bool:
        # Generate a unique user ID for the customer
        customer_id = self.generate_user_id(username)

        # Encrypt the password
        encrypted_password = self.encrypt_password(password, customer_id)

        # Check if the username already exists
        if self.exist_username(username):
            print("Username already exists. Please choose another username.")
            return False

        # Insert the customer data into the database
        query = """
            INSERT INTO tbl_customer (customer_id, username, password, full_name, email, role_id, status, organization_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        role_id = const.ROLE_ID_USER
        status = const.CUSTOMER_STATUS_ACTIVE
        organization_id = const.NULL_VALUE

        values = (customer_id, username, encrypted_password, full_name, email,
                  role_id, status, organization_id)
        try:
            self.db.execute_query(query, values)
            print("Sign-up successful!")
            return True
        except Exception as e:
            print("Error signing up:", e)
            return False

    def forgot_password(self, email: str) -> bool:
        # Generate OTP
        otp = self.generate_otp()

        # Send OTP email
        self.send_email(email, otp)

        # Store OTP in the database with expiration time
        expiration_time = datetime.now() + timedelta(minutes=5)
        query = "INSERT INTO tbl_otp (email, otp, expiration_time) VALUES (%s, %s, %s)"
        values = (email, otp, expiration_time)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error storing OTP:", e)
            return False

    # Function to verify OTP
    def verify_otp(self, email: str, otp: str) -> bool:
        # Check if the OTP matches and has not expired
        current_time = datetime.now()
        query = "SELECT COUNT(*) FROM tbl_otp WHERE email = %s AND otp = %s AND expiration_time >= %s"
        values = (email, otp, current_time)
        result = self.db.execute_query(query, values)
        return result[0][0] > 0

    def delete_used_otp(self, email: str, otp: str) -> None:
        query = "DELETE FROM tbl_otp WHERE email = %s AND otp = %s"
        values = (email, otp)
        try:
            self.db.self.dbect()
            self.db.execute_query(query, values)
            print("Used OTP deleted from the database.")
        except Exception as e:
            print("Error deleting used OTP:", e)
        finally:
            self.db.close()