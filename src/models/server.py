from auth import Auth as auth

class Server:
    def __init__(self,
                 server_name: str = None,
                 host: str = None,
                 organization_id: str = None,
                 server_type: str = None,
                 domain: str = None,
                 rsa_key: str = None,
                 rsa_key_time: str = None,
                 status: str = None) -> None:
        self.server_id = auth.generate_id(server_name)
        self.server_name = server_name
        self.host = host
        self.organization_id = organization_id
        self.server_type = server_type
        self.domain = domain
        self.rsa_key = rsa_key
        self.rsa_key_time = rsa_key_time
        self.status = status
