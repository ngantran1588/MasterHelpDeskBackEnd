from .auth import Auth

class Customer:
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 full_name: str = None,
                 email: str = None,
                 role_id: list[str] = None,
                 status: str = None,
                 organization_id: str = None) -> None:
        auth = Auth()
        self.customer_id = auth.generate_id(username)
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role_id = role_id
        self.status = status
        self.organization_id = organization_id

    
        