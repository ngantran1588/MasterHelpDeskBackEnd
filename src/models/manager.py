from auth import Auth as auth

class Manager:
    def __init__(self,
            manager_username: str = None,
            manager_password: str = None,
            status: str = None,
            role: str = None) -> None:
        self.manager_id = auth.generate_id(manager_username)
        self.manager_username = manager_username
        self.manager_password = manager_password
        self.status = status
        self.role = role