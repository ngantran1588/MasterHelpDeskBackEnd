from datetime import datetime, timedelta, timezone
from . import connector

class BlackListToken:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

    def add_to_blacklist(self, token: str) -> None:
        current_time = datetime.utcnow()
        query = "INSERT INTO tbl_blacklisttoken (token, timestamp) VALUES (%s, %s)"
        values = (token, current_time)
        try:
            self.db.execute_query(query, values)
            return "Token added to blacklist.", 200
        except Exception as e:
            return "Error adding token to blacklist:{e}", 500

    def is_token_blacklisted(self, token: str) -> bool:
        query = "SELECT COUNT(*) FROM tbl_blacklisttoken WHERE token = %s"
        values = (token,)
        try:
            result = self.db.execute_query(query, values)
            return result[0][0] > 0
        except Exception as e:
            print("Error checking token existence in blacklist:", e)
            return False
        
    def remove_expired_tokens(self) -> None:
        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
        query = "DELETE FROM tbl_blacklisttoken WHERE timestamp <= %s"
        values = (two_hours_ago,)
        try:
            self.db.execute_query(query, values)
            return "Expired tokens removed from the blacklist.", 200
        except Exception as e:
            return "Error removing expired tokens from the blacklist:{e}", 500
