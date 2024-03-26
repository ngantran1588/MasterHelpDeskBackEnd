import datetime
import base64

class Organization:
    def __init__(self,
             name: str = None,
             customer_id: str = None,
             organization_status: str = None,
             subscription_id: str = None,
             description: str = None,
             contact_phone: str = None,
             contact_email: str = None,
             expiration_date: datetime = None) -> None:
        self.organization_id = self.generate_user_id(name)
        self.name = name
        self.customer_id = customer_id
        self.organization_status = organization_status
        self.subscription_id = subscription_id
        self.description = description
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.expiration_date = expiration_date


    def generate_organization_id(self, name: str) -> str:
        # Get current time
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
         
        # Combine username and current time
        organization_id = f"{name}_{current_time}"
        
        # Encode organization_id to bytes and then Base64
        organization_id = base64.b64encode(organization_id.encode()).decode()
        
        return organization_id
    
    