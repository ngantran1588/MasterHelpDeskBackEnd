from datetime import datetime, timedelta
from . import connector
from ..const import const
from ..models.auth import Auth as AuthAPI 

class Auth:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.auth = AuthAPI()

    def exist_username(self, username: str) -> bool:
        user_data = self.db.execute_query("SELECT customer_id FROM tbl_customer WHERE username = %s", (username,))
        if user_data is not None and len(user_data) > 0:
            return True
        return False
    
    def exist_email(self, email: str) -> bool:
        user_data = self.db.execute_query("SELECT customer_id FROM tbl_customer WHERE email = %s", (email,))
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
            return self.auth.compare_passwords(customer_id, password, stored_password)
        else:
            return False
    
    def sign_up(self, username: str, password: str, full_name: str, email: str) -> bool:
        # Generate a unique user ID for the customer
        customer_id = self.auth.generate_id(username)

        # Encrypt the password
        encrypted_password = self.auth.encrypt_password(password, customer_id)

        # Check if the username already exists
        if self.exist_username(username):
            msg = "Username already exists. Please choose another username."
            return False, msg
        
        # Check if the email already exists
        if self.exist_email(email):
            msg = "Email already exists. Please choose another email."
            return False, msg
        
        # Insert the customer data into the database
        query = """
            INSERT INTO tbl_customer (customer_id, username, password, full_name, email, role_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        role_id = [const.ROLE_ID_USER]
        status = const.STATUS_INACTIVE

        values = (customer_id, username, encrypted_password, full_name, email,
                  role_id, status)
        try:
            self.db.execute_query(query, values)
            msg = "Sign-up successful!"
            return True, msg
        except Exception as e:
            msg = f"Error signing up:{e}"
            return False, msg

    # Change from User to Super User
    def change_role_to_superuser(self, username: str) -> bool:
        query = "SELECT role_id from tbl_customer WHERE username = %s"
        value = (username,)
        result = self.db.execute_query(query, value)

        try:
            new_role_id = result[0][0]
            new_role_id[0] = const.ROLE_ID_SUPER_USER
            query = "UPDATE tbl_customer SET role_id = %s WHERE username = %s"
            values = (new_role_id, username)

            self.db.execute_query(query, values)
            return "Update role successfully", True
        except Exception as e:
            print("Error changing role:", e)

    # Change from Super User to User
    def change_role_to_user(self, username: str) -> bool:
        query = "SELECT role_id from tbl_customer WHERE username = %s"
        value = (username,)
        result = self.db.execute_query(query, value)
        try:
            new_role_id = result[0][0]
            new_role_id[0] = const.ROLE_ID_USER
            query = "UPDATE tbl_customer SET role_id = %s WHERE username = %s"
            values = (new_role_id, username)

            self.db.execute_query(query, values)
            return "Update role successfully", True
        except Exception as e:
            print("Error changing role:", e)

    def change_role(self, username: str, role_id: list[str]) -> bool:
        query = "SELECT role_id from tbl_customer WHERE username = %s"
        value = (username,)
        result = self.db.execute_query(query, value)
        new_role_id = [result[0][0]]
        new_role_id.append(role_id)

        try:
            query = "UPDATE tbl_customer SET role_id = %s WHERE username = %s"
            values = (new_role_id, username)

            self.db.execute_query(query, values)
            return "Update role successfully", True
        except Exception as e:
            print("Error changing role:", e)

    def send_otp(self, email: str) -> bool:
        
        # Generate OTP
        otp = self.auth.generate_otp()

        # Send OTP email
        self.auth.send_email(email, otp)

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

    # Delete used OTP
    def delete_used_otp(self, email: str, otp: str) -> None:
        query = "DELETE FROM tbl_otp WHERE email = %s AND otp = %s"
        values = (email, otp)
        try:
            self.db.execute_query(query, values)
            print("Used OTP deleted from the database.")
        except Exception as e:
            print("Error deleting used OTP:", e)

    # Delete expired OTP
    def delete_expired_otp(self) -> None:
        current_time = datetime.now()
    
        query = "DELETE FROM tbl_otp WHERE expiration_time < %s"
        value = (current_time,)
        try:
            self.db.execute_query(query, value)
            print("Expired OTP deleted from the database.")
        except Exception as e:
            print("Error deleting expired OTP:", e)

    # Delete all OTP by email
    def delete_otp_email(self, email: str) -> None:
        query = "DELETE FROM tbl_otp WHERE email = %s"
        values = (email)
        try:
            self.db.execute_query(query, values)
            print("OTP from email deleted from the database.")
        except Exception as e:
            print("Error deleting OTP from email:", e)

    # Change password
    def change_password(self, username, new_password, old_password):
        query = "SELECT customer_id, password from tbl_customer WHERE username = %s"
        value = (username,)

        try:
            result = self.db.execute_query(query, value)
            user_id = result[0][0]
            stored_password = result[0][1]
            if not self.auth.compare_passwords(user_id, old_password, stored_password):
                return "Old password is incorrect", False
            
            new_password = self.auth.encrypt_password(new_password, user_id)

            query = "UPDATE tbl_customer SET password = %s WHERE username = %s"
            values = (new_password, username)

            self.db.execute_query(query, values)
            return "Update password successfully", True
        except Exception as e:
            print("Error changing password:", e)

    # Reset password
    def reset_password(self, email, new_password):
        query = "SELECT customer_id from tbl_customer WHERE email = %s"
        value = (email,)

        try:
            result = self.db.execute_query(query, value)
            user_id = result[0][0]
            
            new_password = self.auth.encrypt_password(new_password, user_id)

            query = "UPDATE tbl_customer SET password = %s WHERE email = %s"
            values = (new_password, email)

            self.db.execute_query(query, values)
            return "Update password successfully", True
        except Exception as e:
            print("Error reset password:", e)

    # Get username from email
    def get_username_from_email(self, email: str) -> str:
        query = "SELECT username from tbl_customer WHERE email = %s"
        value = (email,)

        try:
            result = self.db.execute_query(query, value)
            username = result[0][0]

            return username
        except Exception as e:
            print("Error get username from email:", e)

    # Get username from customer id
    def get_username_from_customer_id(self, customer_id: str) -> str:
        query = "SELECT username from tbl_customer WHERE customer_id = %s"
        value = (customer_id,)

        try:
            result = self.db.execute_query(query, value)
            username = result[0][0]

            return username
        except Exception as e:
            print("Error get username from customer_id:", e)

    # Get customer id from username
    def get_customer_id_from_username(self, username: str) -> str:
        query = "SELECT customer_id from tbl_customer WHERE username = %s"
        value = (username,)

        try:
            result = self.db.execute_query(query, value)
            customer_id = result[0][0]

            return customer_id
        except Exception as e:
            print("Error get customer_id from username:", e)

    # Get email from username
    def get_email_from_username(self, username: str) -> str:
        query = "SELECT email from tbl_customer WHERE username = %s"
        value = (username,)

        try:
            result = self.db.execute_query(query, value)
            email = result[0][0]

            return email
        except Exception as e:
            print("Error get email from username:", e)

    def check_role(self, username: str) -> bool:
        try:
            query = "SELECT role_id FROM tbl_customer WHERE username = %s"
            values = (username,)
            result = self.db.execute_query(query, values)
            if result:
                return const.ROLE_ID_SUPER_USER == result[0][0][0]
            else:
                print("User not found or has no roles.")
                return False
        except Exception as e:
            print("Error checking user role:", e)
            return False
        
    def check_role_access(self, username: str, tab: str) -> bool:
        try:
            query = "SELECT role_id FROM tbl_customer WHERE username = %s"
            values = (username,)
            result = self.db.execute_query(query, values)
            if result:
                roles = result[0][0]
                for role in roles:
                    if role == const.ROLE_ID_SUPER_USER:
                        return True
                    elif role == tab.lower():
                        return True
                    return False
            else:
                print("User not found or has no roles.")
                return False
        except Exception as e:
            print("Error checking user role:", e)
            return False
        
    def check_user_pass(self, username: str, input_password: str) -> bool:
        try:
            query = "SELECT customer_id, password FROM tbl_customer WHERE username = %s"
            values = (username,)
            result = self.db.execute_query(query, values)
            
            if result:
                customer_id = result[0][0]
                password = result[0][1]

                if self.auth.compare_passwords(customer_id, input_password, password):
                    return True
                return False 
            else:
                print("User not found")
                return False
        except Exception as e:
            print("Error checking user password:", e)
            return False

    def update_information(self, username: str, full_name: str, email: str):
        try:
            query = """UPDATE tbl_customer SET full_name = %s, email = %s WHERE username = %s"""
            values = (full_name, email, username,)

            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error changing information:", e)
            return False

    def get_profile(self, username: str):
        query = """SELECT customer_id, username, password, full_name, email, role_id, status FROM tbl_customer WHERE username = %s"""
        values = (username,)

        try:
            result = self.db.execute_query(query, values)
            print("Query profile successful!")
            if len(result) == 0:
                return None
            customer_info = result[0]
            customer = {
                "customer_id": customer_info[0],
                "username": customer_info[1],
                "password": customer_info[2],
                "full_name": customer_info[3],
                "email": customer_info[4],
                "role_id": customer_info[5],
                "status": customer_info[6]
            }
               
            return customer
        except Exception as e:
            print("Error querying customer:", e)

    def get_all_profile(self):
        query = """SELECT customer_id, username, full_name, email, status FROM tbl_customer"""

        try:
            result = self.db.execute_query(query)
            print("Query profile successful!")
            if len(result) == 0:
                return None
            customers = []
            for customer_info in result:
                customer = {
                    "customer_id": customer_info[0],
                    "username": customer_info[1],
                    "full_name": customer_info[2],
                    "email": customer_info[3],
                    "status": customer_info[4]
                }
                customers.append(customer)
            return customers
        except Exception as e:
            print("Error querying customer:", e)

    def get_profile_by_id(self, customer_id: str):
        query = """SELECT customer_id, username, full_name, email, status FROM tbl_customer WHERE customer_id = %s"""
        value = (customer_id,)
        try:
            result = self.db.execute_query(query, value)
            print("Query profile successful!")
            if len(result) == 0:
                return None
            customer_info = result[0]
            customer = {
                "customer_id": customer_info[0],
                "username": customer_info[1],
                "full_name": customer_info[2],
                "email": customer_info[3],
                "status": customer_info[4]
            }
            return customer
        except Exception as e:
            print("Error querying customer:", e)
    
    def is_inactive_user(self, username: str) -> bool:
        try:
            # Check if the user with the given username is inactive
            query = "SELECT status FROM tbl_customer WHERE username = %s"
            values = (username,)
            result = self.db.execute_query(query, values)
            if result:
                return result[0][0] == const.STATUS_INACTIVE
            else:
                print("User not found.")
                return False
        except Exception as e:
            print("Error checking user status:", e)
            return False

    def change_status(self, username: str, new_status: str) -> bool:
        if new_status.upper() == const.STATUS_ACTIVE:
            new_status = const.STATUS_ACTIVE
        elif new_status.upper() == const.STATUS_INACTIVE:
            new_status = const.STATUS_INACTIVE
        else:
            return "status is incorrect", False

        try:
            query = "UPDATE tbl_customer SET new_status = %s WHERE username = %s"
            values = (new_status, username)

            self.db.execute_query(query, values)
            return "Update status successfully", True
        except Exception as e:
            print("Error changing status:", e)

    def get_role_by_username(self, username: str):
        query = "SELECT role_id from tbl_customer WHERE username = %s"
        value = (username,)

        try:
            result = self.db.execute_query(query, value)
            role = result[0][0]

            return role
        except Exception as e:
            print("Error get role from username:", e)      
            return None
    
    def get_role_of_members(self, list_username):
        return_list = []
        for username in list_username:
            role = self.get_role_by_username(username)
            if role == None:
                return None
            data = {"username": username, "role": role}
            return_list.append(data)

        return return_list
        
