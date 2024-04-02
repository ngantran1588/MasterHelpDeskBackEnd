from datetime import datetime
from . import connector
from ..const import const
import hashlib
from ..models.server import Server as ServerModel

class Server:
    def __init__(self, db: connector.DBConnector):
        self.db = db
        self.db.connect()
        self.server = ServerModel()

    def add_server(self, server_id: str, server_name: str, host: str, organization_id: str,
               server_type: str, domain: str, rsa_key: str, rsa_key_time: str,
               status: str) -> bool:
        query = """
            INSERT INTO tbl_server (
                server_id, server_name, host, organization_id,
                server_type, domain, rsa_key, rsa_key_time, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            server_id, server_name, host, organization_id,
            server_type, domain, self.encrypt_rsa_key(rsa_key), rsa_key_time,
            status
        )
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error adding server:", e)
            return False


    def update_rsa_key(self, server_id: str, new_rsa_key: str) -> bool:
        encrypted_rsa_key = self.encrypt_rsa_key(new_rsa_key)
        query = "UPDATE tbl_server SET rsa_key = %s WHERE server_id = %s"
        values = (encrypted_rsa_key, server_id)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error updating RSA key:", e)
            return False

    def update_rsa_key_time(self, server_id: str, new_rsa_key_time: datetime) -> bool:
        query = "UPDATE tbl_server SET rsa_key_time = %s WHERE server_id = %s"
        values = (new_rsa_key_time, server_id)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error updating RSA key time:", e)
            return False

    def check_rsa_key_time_due(self, server_id: str) -> bool:
        query = "SELECT rsa_key_time FROM tbl_server WHERE server_id = %s"
        values = (server_id,)
        try:
            rsa_key_time = self.db.execute_query(query, values)[0][0]
            # Implement logic to check if RSA key time is due
            return True
        except Exception as e:
            print("Error checking RSA key time due:", e)
            return False

    def delete_server(self, server_id: str) -> bool:
        query = "DELETE FROM tbl_server WHERE server_id = %s"
        values = (server_id,)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error deleting server:", e)
            return False

    def update_other_fields(self, server_id: str, **kwargs) -> bool:
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE tbl_server SET {set_clause} WHERE server_id = %s"
        values = list(kwargs.values()) + [server_id]
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error updating other fields:", e)
            return False

    def update_status(self, server_id: str, new_status: str) -> bool:
        query = "UPDATE tbl_server SET status = %s WHERE server_id = %s"
        values = (new_status, server_id)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error updating status:", e)
            return False

    def encrypt_rsa_key(self, rsa_key: str) -> str:
        hashed_key = hashlib.sha256(rsa_key.encode()).hexdigest()
        return hashed_key

    def decrypt_rsa_key(self, hashed_key: str) -> str:
        # This is a one-way encryption (hashing), so decryption is not possible.
        return None
