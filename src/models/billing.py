from datetime import datetime

class Billing:
    def __init__(self,
                 billing_id: str = None,
                 customer_id: str = None,
                 subscription_id: int = None,
                 timestamp: datetime = None,
                 billing_status: str = None,
                 amount: float = None,
                 signature: str = None) -> None:
        self.billing_id = billing_id
        self.customer_id = customer_id
        self.subscription_id = subscription_id
        self.timestamp = timestamp
        self.billing_status = billing_status
        self.amount = amount
        self.signature = signature