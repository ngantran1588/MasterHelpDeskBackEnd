from datetime import datetime, timezone
from . import connector
from ..const import const
from ..models.auth import Auth as AuthAPI

class Subscription:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.auth = AuthAPI()

    def check_subscription_by_username(self, username: str) -> bool:
        query_customer = """SELECT customer_id FROM tbl_customer WHERE username = %s"""
        value_customer = (username,)
        customer_data = self.db.execute_query(query_customer, value_customer)
        try:
            query = """SELECT subscription_id FROM tbl_subscription WHERE customer_id = %s"""
            value = (customer_data[0])
            result = self.db.execute_query(query, value)
            
            if result:
                return True
            return False
        except Exception as e:
            print("Error querying guides:", e)
            return False
        
    def add_subscription(self, subscription_name: str, customer_id: str, subscription_type: str, expiration_date: datetime, renewable: bool = False) -> None:
        try:
            subscription_id = self.auth.generate_id(customer_id)
            subscription_status = const.STATUS_ACTIVE
            query = """
                INSERT INTO tbl_subscription (subscription_id, subscription_name, customer_id, subscription_type, expiration_date, renewable, subscription_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (subscription_id, subscription_name, customer_id, subscription_type, expiration_date, renewable, subscription_status)
            self.db.execute_query(query, values)
            print("Subscription added successfully.")
            return subscription_id
        except Exception as e:
            print("Error adding subscription:", e)
            return None

    def update_subscription_status(self, subscription_id: str, new_status: str) -> None:
        try:
            query = "UPDATE tbl_subscription SET subscription_status = %s WHERE subscription_id = %s"
            values = (new_status, subscription_id)
            self.db.execute_query(query, values)
            print("Subscription status updated successfully.")
        except Exception as e:
            print("Error updating subscription status:", e)

    def check_renewal(self, expiration_date: datetime) -> str:
        try:
            time_diff = expiration_date - datetime.now(timezone.utc)
            if time_diff.days <= 2 and time_diff.days > 1:
                return "2 days left for renewal"
            elif time_diff.days == 1:
                return "1 day left for renewal"
            elif time_diff.days <= 0:
                return "Subscription expired"
            else:
                return "Subscription active"
        except Exception as e:
            return "Error checking renewal"
        
    def get_subscription_by_id(self, subscription_id: str):
        try:
            query = """SELECT subscription_id, subscription_name, renewable, subscription_type, subscription_status, expiration_date 
                       FROM tbl_subscription WHERE subscription_id = %s"""
            values = (subscription_id,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None

            subscription_info = result[0]
            subscription = {
                "subscription_id": subscription_info[0],
                "subscription_name": subscription_info[1],
                "renewable": subscription_info[2],
                "subscription_type": subscription_info[3],
                "subscription_status": subscription_info[4],
                "expiration_date": subscription_info[5].strftime("%Y-%m-%d %H:%M:%S") if subscription_info[5] else None,
            }

            return subscription
        except Exception as e:
            print("Error fetching subscription record:", e)
            return None
        
    def get_all_subscriptions(self):
        try:
            query = """SELECT subscription_id, subscription_name, renewable, subscription_type, subscription_status, expiration_date 
                       FROM tbl_subscription"""
            result = self.db.execute_query(query)

            if len(result) == 0:
                return None

            subscriptions = []
            for subscription_info in result:
                subscription = {
                    "subscription_id": subscription_info[0],
                    "subscription_name": subscription_info[1],
                    "renewable": subscription_info[2],
                    "subscription_type": subscription_info[3],
                    "subscription_status": subscription_info[4],
                    "expiration_date": subscription_info[5].strftime("%Y-%m-%d %H:%M:%S") if subscription_info[5] else None,
                }
                subscriptions.append(subscription)

            return subscriptions
        except Exception as e:
            print("Error fetching all subscriptions:", e)
            return None
        
    def get_subscription_by_status(self, status: str):
        try:
            query = """SELECT subscription_id, subscription_name, renewable, subscription_type, subscription_status, expiration_date 
                       FROM tbl_subscription WHERE subscription_status = %s"""
            values = (status,)
            result = self.db.execute_query(query, values)

            if len(result) == 0:
                return None

            subscriptions = []
            for subscription_info in result:
                subscription = {
                    "subscription_id": subscription_info[0],
                    "subscription_name": subscription_info[1],
                    "renewable": subscription_info[2],
                    "subscription_type": subscription_info[3],
                    "subscription_status": subscription_info[4],
                    "expiration_date": subscription_info[5].strftime("%Y-%m-%d %H:%M:%S") if subscription_info[5] else None,
                }
                subscriptions.append(subscription)

            return subscriptions
        except Exception as e:
            print("Error fetching subscriptions by status:", e)
            return None