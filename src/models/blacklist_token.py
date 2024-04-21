from datetime import datetime

class BlacklistToken:
    def __init__(self, token: str, timestamp: datetime) -> None:
        self.token = token
        self.timestamp = timestamp