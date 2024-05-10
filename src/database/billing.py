from datetime import datetime, timezone
import os
import hmac
import hashlib
from . import connector
from ..const import const
from ..models.auth import Auth as AuthAPI

class Billing:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()
        self.auth = AuthAPI()

    def add_billing(self, customer_id: str, amount: float) -> None:
        try:
            billing_id = self.auth.generate_id(customer_id)
            timestamp = datetime.now(timezone.utc)
            billing_status = const.BILLING_STATUS_PENDING
            subscription_id = const.NULL_VALUE

            secret_key = os.environ.get("SECRET_KEY")
            access_key = os.environ.get("MOMO_ACCESS_KEY")
            ipn_url = os.environ.get("IPN_URL")
            redirect_url = os.environ.get("REDIRECT_URL")
            partner_code = os.environ.get("MOMO_PARTNER_CODE")
            data = {
                "accessKey": access_key,
                "amount": amount,
                "extraData": "",
                "ipnUrl": ipn_url,
                "orderId": billing_id,
                "orderInfo": customer_id,
                "partnerCode": partner_code,
                "redirectUrl": redirect_url,
                "requestId": billing_id,
                "requestType": "captureWallet"
            }

            signature = self.create_signature(secret_key, data)
            return_data = {
                "partnerCode": partner_code,
                "requestType": "captureWallet",
                "ipnUrl": ipn_url,
                "redirectUrl": redirect_url,
                "orderId": billing_id,
                "amount": amount,
                "lang":  "en",
                "orderInfo": customer_id,
                "requestId": billing_id,
                "extraData": "",
                "signature": signature
            }

            query = """INSERT INTO tbl_billing (billing_id, customer_id, subscription_id, timestamp, billing_status, amount, signature) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (billing_id, customer_id, subscription_id, timestamp, billing_status, amount, signature)
            self.db.execute_query(query, values)
            print("Billing record added successfully.")
            
            return return_data
        except Exception as e:
            print("Error adding billing record:", e)
            return None

    def create_signature(secret_key: str, data: dict):
        # Sort the data dictionary by keys and concatenate key-value pairs
        sorted_values = "&".join([f"{key}={data[key]}" for key in sorted(data.keys())])
        
        # Create the HMAC-SHA256 signature using the secret key and sorted values
        h = hmac.new(bytes(secret_key, "ascii"), bytes(sorted_values, "ascii"), hashlib.sha256)
        signature = h.hexdigest()

        return signature
    
    def check_signature(self, billing_id: str, signature: str):
        try:
            query = """SELECT signature FROM tbl_billing WHERE billing_id = %s"""
            values = (billing_id,)
            signature_db = self.db.execute_query(query, values)[0][0]
            if signature == signature_db:
                return True
            return False
            
        except Exception as e:
            return False


    def delete_billing(self, billing_id: str) -> None:
        try:
            query = """DELETE FROM tbl_billing WHERE billing_id = %s"""
            values = (billing_id,)
            self.db.execute_query(query, values)
            print("Billing record deleted successfully.")
        except Exception as e:
            print("Error deleting billing record:", e)

    def update_billing_status(self, billing_id: str, new_status: str) -> None:
        try:
            query = """UPDATE tbl_billing SET billing_status = %s WHERE billing_id = %s"""
            values = (new_status, billing_id)
            self.db.execute_query(query, values)
            print("Billing status updated successfully.")
        except Exception as e:
            print("Error updating billing status:", e)
    
    def update_success_transaction(self, billing_id: str, new_status: str, subscription_id: str) -> None:
        try:
            query = """UPDATE tbl_billing SET billing_status = %s, subscription_id = %s WHERE billing_id = %s"""
            values = (new_status, subscription_id, billing_id)
            self.db.execute_query(query, values)
            print("Billing status updated successfully.")
        except Exception as e:
            print("Error updating billing:", e)

    def get_billing_by_id(self, billing_id: str):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE billing_id = %s"""
            values = (billing_id,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            
            billing_info = result[0]
            billing = {
                "billing_id": billing_info[0],
                "customer_id": billing_info[1],
                "subscription_id": billing_info[2],
                "timestamp": billing_info[3],
                "billing_status": billing_info[4],
                "amount": billing_info[5],
            }

            return billing
        except Exception as e:
            print("Error fetching billing record:", e)
            return None

    def get_all_billing(self):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing"""
            result = self.db.execute_query(query)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching all billing records:", e)
            return None

    def get_billing_by_customer_id(self, username: str):
        try:
            query_username = """SELECT customer_id FROM tbl_customer WHERE username = %s"""
            value = (username,)
            customer_id = self.db.execute_query(query_username, value)[0][0]

            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE customer_id = %s"""
            values = (customer_id,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching billing records by customer ID:", e)
            return None

    def get_billing_by_status(self, status: str):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE billing_status = %s"""
            values = (status,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching billing records by status:", e)
            return None
    
    def get_billing_status_by_customer_id(self, status: str, customer_id: str):
        try:
            query = """SELECT billing_id, customer_id, subscription_id, timestamp, billing_status, amount FROM tbl_billing WHERE billing_status = %s AND customer_id = %s"""
            values = (status, customer_id,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None
            billings = []
            for billing_info in result:
                # Extract billings information and create a dictionary
                billing = {
                    "billing_id": billing_info[0],
                    "customer_id": billing_info[1],
                    "subscription_id": billing_info[2],
                    "timestamp": billing_info[3],
                    "billing_status": billing_info[4],
                    "amount": billing_info[5],
                }
                billings.append(billing)

            return billings
        except Exception as e:
            print("Error fetching billing records by status:", e)
            return None