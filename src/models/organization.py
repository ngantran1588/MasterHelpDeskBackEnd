from .auth import Auth as auth

class Organization:
    def __init__(self,
             name: str = None,
             customer_id: str = None,
             organization_status: str = None,
             subscription_id: str = None,
             description: str = None,
             contact_phone: str = None,
             contact_email: str = None,
             org_member: list[str] = None) -> None:
        self.organization_id = auth.generate_id(name)
        self.name = name
        self.customer_id = customer_id
        self.organization_status = organization_status
        self.subscription_id = subscription_id
        self.description = description
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.org_member = org_member

    
    