from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import ast
from . import connector
from ..const import const
from ..models.server import Server as ServerModel
from ..models.auth import Auth 
import os 
from dotenv import load_dotenv

load_dotenv()

class Server:
    def __init__(self, db: connector.DBConnector):
        self.db = db
        self.server = ServerModel()
        self.auth = Auth()

    def add_server(self, user_create_server: str, server_name: str, hostname: str, organization_id: str,
               username: str, password: str, rsa_key: str, port: str) -> bool:
        query = """
            INSERT INTO tbl_server (
                server_id, server_name, hostname, organization_id,
                username, password, rsa_key, authen_key_time, status, member, port
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        server_member = []

        server_id = self.auth.generate_id(server_name)
        status = const.STATUS_ACTIVE
        passphrase = os.environ.get("RSA_PASSPHRASE")

        if password != None and password != "":
            password = self.encrypt_rsa_key(passphrase.encode(), server_id.encode(), password)
        else:
            password = const.NULL_VALUE
        
        if rsa_key != None and rsa_key != "":
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
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce.encode()))
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
            
            return current_slot >= total_slot
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
            passphrase = os.environ.get("RSA_PASSPHRASE")

            return self.decrypt_rsa_key(passphrase.encode(), server_id.encode(), server_info[0])
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
        query = "SELECT COUNT(*) FROM tbl_server WHERE organization_id = %s"
        values = (organization_id,)
        try:
            result = self.db.execute_query(query, values)
            return result[0][0]
        except Exception as e:
            print("Error getting server number:", e)
            return False
        
    def get_server_in_organization(self, organization_id: str):
        query = "SELECT server_id, server_name, status, hostname FROM tbl_server WHERE organization_id = %s"
        values = (organization_id,)
        try:
            result = self.db.execute_query(query, values)
            servers = []
            for server_info in result:
                server = {
                    "server_id": server_info[0],
                    "server_name": server_info[1],
                    "status": server_info[2],
                    "hostname": server_info[3],
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
        
    def add_user(self, server_id: str, new_user: str) -> bool:
        # Query to fetch the current member list of the server
        select_query = "SELECT member FROM tbl_server WHERE server_id = %s"
        select_values = (server_id,)
        
        try:
            # Fetch the current member list from the database
            current_members = self.db.execute_query(select_query, select_values)
            if current_members:
                current_member_list = current_members[0][0]
                
                # Check if the new user is already a member of the server
                if new_user in current_member_list:
                    print(f"User '{new_user}' already exists in the server.")
                    return False
                
                # Add the new user to the server's member list
                current_member_list.append(new_user)

                # Update the server's member list in the database
                update_query = "UPDATE tbl_server SET member = %s WHERE server_id = %s"
                update_values = (current_member_list, server_id)
                self.db.execute_query(update_query, update_values)

                msg = "Users added to server successfully!"
                return True, msg
            else:
                msg = "server not found."
                return False, msg
        except Exception as e:
            msg = f"Error adding user(s) to server: {e}"
            return False, msg
   
    def remove_user(self, server_id: str, remove_username: str) -> bool:
        try:
            # Fetch the current member list of the server from the database
            select_query = "SELECT member FROM tbl_server WHERE server_id = %s"
            select_values = (server_id,)
            result = self.db.execute_query(select_query, select_values)
            
            if result:
                member_list = result[0][0]
                creator_username = member_list[0]
                
                # Check if the user to be removed is the creator of the server
                if remove_username == creator_username:
                    msg = "Cannot remove the creator of the server."
                    return False, msg
                
                # Check if the member list will have at least one member after removal
                if len(member_list) == 1:
                    msg = "Cannot remove the last member of the server."
                    return False, msg
                
                # Check if the user to be removed is in the member list
                if remove_username not in member_list:
                    msg = f"User '{remove_username}' is not a member of the server."
                    return False, msg
                
                # Remove the user from the member list
                member_list.remove(remove_username)
                
                # Update the member list in the database
                update_query = "UPDATE tbl_server SET member = %s WHERE server_id = %s"
                update_values = (member_list, server_id)
                self.db.execute_query(update_query, update_values)
                
                msg = "User removed from server successfully!"
                return True, msg
            else:
                msg = "server not found."
                return False, msg
        except Exception as e:
            msg = f"Error removing user from server:{e}"
            return False, msg
        
    def get_info_to_connect(self, server_id: str):
        query = "SELECT hostname, username, password, rsa_key FROM tbl_server WHERE server_id = %s"
        values = (server_id,)
        try:
            result = self.db.execute_query(query, values)
            passphrase = os.environ.get("RSA_PASSPHRASE")
            if result[0][2] != const.NULL_VALUE:
                pass_from_db = result[0][2]
                pass_encrypted = ast.literal_eval(pass_from_db)
                password = self.decrypt_rsa_key(passphrase.encode(), server_id.encode(), pass_encrypted)
            else:
                password = None

            if result[0][3] != const.NULL_VALUE:
                rsa_key_from_db = result[0][3]
                rsa_key_encrypted = ast.literal_eval(rsa_key_from_db)
                rsa_key = self.decrypt_rsa_key(passphrase.encode(), server_id.encode(), rsa_key_encrypted)
            else:
                rsa_key = None

            server = {
                "server_id": server_id,
                "hostname": result[0][0],
                "username": result[0][1],
                "password": password,
                "rsa_key": rsa_key,
            }
            return server
        except Exception as e:
            print("Error getting server info:", e)
            return False
        
    def get_server_members(self, server_id: str) -> list:
        # Query to fetch the current member list of the server
        select_query = "SELECT member FROM tbl_server WHERE server_id = %s"
        select_values = (server_id,)

        try:
            # Fetch the current member list from the database
            current_members = self.db.execute_query(select_query, select_values)
            if current_members:
                return current_members[0][0]
            else:
                return []  # Return an empty list if server not found or no members
        except Exception as e:
            print(f"Error fetching server members: {e}")
            return []