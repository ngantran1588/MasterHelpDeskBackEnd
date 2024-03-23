from auth import Auth as auth

class Customer:
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 full_name: str = None,
                 email: str = None,
                 role_id: str = None,
                 status: str = None,
                 organization_id: str = None) -> None:
        self.customer_id = auth.generate_user_id(username)
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role_id = role_id
        self.status = status
        self.organization_id = organization_id

    
        