from .auth import Auth

class Server:
    def __init__(self,
                 server_name: str = None,
                 hostname: str = None,
                 username: str = None,
                 password: str = None,
                 organization_id: str = None,
                 rsa_key: str = None,
                 authen_key_time: str = None,
                 status: str = None,
                 member: list[str] = None,
                 port: str = None) -> None:
        auth = Auth()
        self.server_id = auth.generate_id(server_name)
        self.server_name = server_name
        self.hostname = hostname
        self.username = username
        self.password = password
        self.organization_id = organization_id
        self.rsa_key = rsa_key
        self.authen_key_time = authen_key_time
        self.status = status
        self.member = member
        self.port = port
