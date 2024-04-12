from auth import Auth as auth
from datetime import datetime

class Subscription:
    def __init__(self,
                 subscription_id: str = None,
                 subscription_name: str = None,
                 renewable: bool = None,
                 subscription_type: str = None,
                 subscription_status: str = None,
                 customer_id: str = None,
                 expiration_date: datetime = None) -> None:
        self.subscription_id = subscription_id
        self.subscription_name = subscription_name
        self.renewable = renewable
        self.subscription_type = subscription_type
        self.subscription_status = subscription_status
        self.customer_id = customer_id
        self.expiration_date = expiration_date

