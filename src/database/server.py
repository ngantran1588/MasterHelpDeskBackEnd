from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from . import connector
from ..const import const
import hashlib
from ..models.server import Server as ServerModel
from ..models.auth import Auth 
import os 
from dotenv import load_dotenv

load_dotenv()

class Server:
    def __init__(self, db: connector.DBConnector):
        self.db = db
        self.db.connect()
        self.server = ServerModel()
        self.auth = Auth()

    def add_server(self, user_create_server: str, server_name: str, hostname: str, organization_id: str,
               username: str, password: str, rsa_key: str, port: str) -> bool:
        query = """
            INSERT INTO tbl_server (
                server_id, server_name, hostname, organization_id,
                username, password, rsa_key, authen_key_time, status, member, port
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        server_member = []

        server_id = self.auth.generate_id(server_name)
        status = const.STATUS_ACTIVE
        passphrase = os.environ.get("RSA_PASSPHRASE")

        if password != None or password != "":
            password = self.encrypt_rsa_key(passphrase.encode(), server_id.encode(), password)
        else:
            password = const.NULL_VALUE
        
        if rsa_key != None or rsa_key != "":
            rsa_key = self.encrypt_rsa_key(passphrase.encode(), server_id.encode(), rsa_key)
        else:
            rsa_key = const.NULL_VALUE

        authen_key_time = datetime.now() + timedelta(days=30)

        server_member.append(user_create_server)

        if port == None or port == "":
            port = const.NULL_VALUE

        values = (str(server_id), server_name, str(hostname), str(organization_id), username, str(password), str(rsa_key), authen_key_time,status, server_member, port,)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error adding server:", e)
            return False

    def update_password_key(self, server_id: str, password: str) -> bool:
        passphrase = os.environ.get("RSA_PASSPHRASE")
        encrypted_password_key = self.encrypt_rsa_key(passphrase.encode(), server_id.encode(), password)
        query = "UPDATE tbl_server SET password = %s WHERE server_id = %s"
        values = (encrypted_password_key, server_id)
        try:
            self.db.execute_query(query, values)
            new_authen_key_time = datetime.now() + timedelta(days=30)
            self.update_authen_key_time(server_id, new_authen_key_time)
            return True
        except Exception as e:
            print("Error updating Password key:", e)
            return False

    def update_rsa_key(self, server_id: str, new_rsa_key: str) -> bool:
        passphrase = os.environ.get("RSA_PASSPHRASE")
        encrypted_rsa_key = self.encrypt_rsa_key(passphrase.encode(), server_id.encode(), new_rsa_key)
        query = "UPDATE tbl_server SET rsa_key = %s WHERE server_id = %s"
        values = (encrypted_rsa_key, server_id)
        try:
            self.db.execute_query(query, values)
            new_authen_key_time = datetime.now() + timedelta(days=30)
            self.update_authen_key_time(server_id, new_authen_key_time)
            return True
        except Exception as e:
            print("Error updating RSA key:", e)
            return False

    def update_authen_key_time(self, server_id: str, new_authen_key_time: datetime) -> bool:
        query = "UPDATE tbl_server SET authen_key_time = %s WHERE server_id = %s"
        values = (new_authen_key_time, server_id)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error updating RSA key time:", e)
            return False

    def check_authen_key_time_due(self, server_id: str) -> bool:
        query = "SELECT authen_key_time FROM tbl_server WHERE server_id = %s"
        values = (server_id,)
        try:
            authen_key_time_str = self.db.execute_query(query, values)[0][0]
            authen_key_time = datetime.fromisoformat(authen_key_time_str)
            current_time = datetime.now()
            if current_time > authen_key_time:
                return True
            else:
                return False
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

    def update_server_information(self, server_id: str, server_name: str, hostname: str, username: str, port: str) -> bool:

        if port == None or port == "":
            port = const.NULL_VALUE

        query = """ UPDATE tbl_server SET server_name = %s, hostname = %s, username = %s, port = %s WHERE server_id = %s"""
        values = (server_name, hostname, username, server_id, port)
        try:
            self.db.execute_query(query, values)
            print("Server information updated successfully!")
            return True
        except Exception as e:
            print("Error updating server information:", e)
            return False


    def update_status(self, server_id: str, new_status: str) -> bool:
        query = "UPDATE tbl_server SET status = %s WHERE server_id = %s"
        if new_status == const.STATUS_INACTIVE:
            values = (const.STATUS_INACTIVE, server_id)
        else :
            values = (const.STATUS_ACTIVE, server_id)
        try:
            self.db.execute_query(query, values)
            return True
        except Exception as e:
            print("Error updating status:", e)
            return False

    def derive_key(self, passphrase: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(passphrase)

    def encrypt_rsa_key(self, passphrase: bytes, salt: bytes, rsa_key: str) -> bytes:
        nonce = os.environ.get("NONCE")
        key = self.derive_key(passphrase, salt)
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce.encode()))
        encryptor = cipher.encryptor()
        rsa_key_encrypted = encryptor.update(rsa_key.encode()) + encryptor.finalize()
        return rsa_key_encrypted

    def decrypt_rsa_key(self, passphrase: bytes, salt: bytes, rsa_key_encrypted: bytes) -> str:
        nonce = os.environ.get("NONCE")
        key = self.derive_key(passphrase, salt)
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
        decryptor = cipher.decryptor()
        rsa_key_decrypted = decryptor.update(rsa_key_encrypted) + decryptor.finalize()
        return rsa_key_decrypted.decode()

    def check_server_slot(self, organization_id: str):
        try:
            # Get customer_id from tbl_organization using organization_id
            query_customer_id = "SELECT customer_id FROM tbl_organization WHERE organization_id = %s"
            values_customer_id = (organization_id,)
            customer_id = self.db.execute_query(query_customer_id, values_customer_id)[0][0]

            # Get subscription_type from tbl_subscription
            query_subscription = "SELECT subscription_type FROM tbl_subscription WHERE customer_id = %s"
            values_subscription = (customer_id,)
            subscription_type = self.db.execute_query(query_subscription, values_subscription)[0][0]

            # Get slot from tbl_package
            query_slot = "SELECT slot_server FROM tbl_package WHERE package_id = %s"
            values_slot = (subscription_type,)
            total_slot = self.db.execute_query(query_slot, values_slot)[0][0]

            # Count current server for organization_id
            query_count_server = "SELECT COUNT(*) FROM tbl_server WHERE organization_id = %s"
            values_count_server = (organization_id,)
            current_slot = self.db.execute_query(query_count_server, values_count_server)[0][0]
            
            return current_slot > total_slot
        except Exception as e:
            print("Error checking server slot:", e)
            return False

    def get_rsa_key(self, server_id: str):
        query = """SELECT rsa_key FROM tbl_server WHERE server_id = %s"""
        values = (server_id,)

        try:
            result = self.db.execute_query(query, values)
            print("Query server successful!")
            if len(result) == 0:
                return None
            server_info = result[0]
            
            return self.decrypt_rsa_key(server_info["rsa_key"])
        except Exception as e:
            print("Error querying server:", e)

    def get_server_data(self, server_id: str):
        query = """SELECT server_id, server_name, hostname, organization_id, username, password, rsa_key, authen_key_time, status, member, port FROM tbl_server WHERE server_id = %s"""
        values = (server_id,)

        try:
            result = self.db.execute_query(query, values)
            print("Query server successful!")
            if len(result) == 0:
                return None
            server_info = result[0]
            
            server = {
                "server_id": server_info[0],
                "server_name": server_info[1],
                "hostname": server_info[2],
                "organization_id": server_info[3],
                "username": server_info[4],
                "password": server_info[5],
                "rsa_key": server_info[6],
                "authen_key_time": server_info[7],
                "status": server_info[8],
                "member": server_info[9],
                "port": server_info[10]
            }

            return server
        except Exception as e:
            print("Error querying server:", e)

    def get_server_by_id(self, server_id: str):
        query = """SELECT server_name, status, hostname FROM tbl_server WHERE server_id = %s"""
        values = (server_id,)

        try:
            result = self.db.execute_query(query, values)
            print("Query server successful!")
            if len(result) == 0:
                return None
            server_info = result[0]
            
            server = {
                "server_id": server_id,
                "server_name": server_info[0],
                "status": server_info[1],
                "hostname": server_info[2]
            }
                
            return server
        except Exception as e:
            print("Error querying server:", e)

    def get_number_server(self, organization_id: str):
        query = "SELECT server_id FROM tbl_server WHERE organization_id = %s"
        values = (organization_id,)
        try:
            result = self.db.execute_query(query, values)
            return len(result[0][0])
        except Exception as e:
            print("Error getting server number:", e)
            return False
        
    def get_server_in_organization(self, organization_id: str):
        query = "SELECT server_id, server_name, status FROM tbl_server WHERE organization_id = %s"
        values = (organization_id,)
        try:
            result = self.db.execute_query(query, values)
            servers = []
            for server_info in result:
                server = {
                    "server_id": server_info[0],
                    "server_name": server_info[1],
                    "status": server_info[2],
                }
                servers.append(server)
            return servers
        except Exception as e:
            print("Error getting server number:", e)
            return False
    
    def check_server_name_exist(self, name: str, organization_id: str) -> bool:
        query = "SELECT COUNT(*) FROM tbl_server WHERE server_name = %s AND organization_id = %s"
        values = (name, organization_id,)
        try:
            result = self.db.execute_query(query, values)
            return result[0][0] > 0
        except Exception as e:
            print("Error checking server name existence:", e)
            return False

    def check_user_access(self, username: str, server_id: str) -> bool:
        query = """ SELECT COUNT(*) FROM tbl_server WHERE server_id = %s AND  %s = ANY(member) """
        values = (server_id, username,)
        try:
            result = self.db.execute_query(query, values)
            access_granted = result[0][0] > 0
            return access_granted
        except Exception as e:
            print("Error checking user access:", e)
            return False
        
    def add_user(self, server_id: str, new_user: list[str]) -> bool:
        query = """ UPDATE tbl_server SET member = array_append(member, %s) WHERE server_id = %s"""
        values = (new_user, server_id,)
        try:
            self.db.execute_query(query, values)
            print("User added to server successfully!")
            return True
        except Exception as e:
            print("Error adding user to server:", e)
            return False

    def remove_user(self, server_id: str, remove_username: str) -> bool:
        query = """UPDATE tbl_server SET member = array_remove(member, %s) WHERE server_id = %s"""
        values = (remove_username, server_id,)
        try:
            self.db.execute_query(query, values)
            print("User removed from server successfully!")
            return True
        except Exception as e:
            print("Error removing user from server:", e)
            return False
        
    def get_info_to_connect(self, server_id: str):
        query = "SELECT hostname, username, password, rsa_key FROM tbl_server WHERE server_id = %s"
        values = (server_id,)
        try:
            result = self.db.execute_query(query, values)
         
            server = {
                "server_id": server_id,
                "hostname": result[0][0],
                "username": result[0][1],
                "password": result[0][2],
                "rsa_key": result[0][3],
            }
            return server
        except Exception as e:
            print("Error getting server info:", e)
            return False