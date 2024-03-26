from datetime import datetime, timedelta
import connector
from ..const import const
from ..models.organization import Organization as organization

class Organization:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

    def add_organization(self, name: str, contact_phone: str, contact_email: str, description: str, username: str) -> bool:
        # # Generate a unique user ID for the customer
        # customer_id = self.generate_user_id(username)

        # # Encrypt the password
        # encrypted_password = self.encrypt_password(password, customer_id)

        # # Check if the username already exists
        # if self.exist_username(username):
        #     print("Username already exists. Please choose another username.")
        #     return False
        # role_id = const.ROLE_ID_USER
        # status = const.CUSTOMER_STATUS_ACTIVE
        # organization_id = const.NULL_VALUE

        # values = (customer_id, username, encrypted_password, full_name, email,
        #           role_id, status, organization_id)
        # try:
        #     self.db.execute_query(query, values)
        #     print("Sign-up successful!")
        #     return True
        # except Exception as e:
        #     print("Error signing up:", e)
        #     return False
        organization_id = self.generate_organization_id(name)
        organization_status = const.STATUS_ACTIVE

        query_user = """SELECT customer_id FROM tbl_customer WHERE username = %s"""
        value_user = (username,)

        user_data = self.db.execute_query(query_user, value_user)

        if len(user_data) == 0:
            print("Error in querying user data")
            return False

        query = """
            INSERT INTO tbl_organization (
                organization_id, name, customer_id, organization_status,
                subscription_id, description, contact_phone, contact_email,
                expiration_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (organization_id, name, user_data[0], organization_status, "subscriptionid", description)