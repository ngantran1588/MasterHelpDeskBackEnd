from datetime import datetime, timedelta
from . import connector
from ..const import const
from ..models.auth import Auth as AuthAPI

class Subscription:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()
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