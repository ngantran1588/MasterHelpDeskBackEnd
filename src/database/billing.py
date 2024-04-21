from datetime import datetime
from . import connector
from ..const import const

class Billing:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

    def add_billing(self, customer_id: str, subscription_id: int, amount: float) -> None:
        try:
            billing_id = self.generate_billing_id(customer_id)
            timestamp = datetime.utcnow()
            billing_status = const.BILLING_STATUS_PENDING

            query = """INSERT INTO tbl_billing (billing_id, customer_id, subscription_id, timestamp, billing_status, amount) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            values = (billing_id, customer_id, subscription_id, timestamp, billing_status, amount)
            self.db.execute_query(query, values)
            print("Billing record added successfully.")
        except Exception as e:
            print("Error adding billing record:", e)

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

    def generate_billing_id(self, customer_id: str) -> str:
        # Implement your unique ID generation logic here
        pass
