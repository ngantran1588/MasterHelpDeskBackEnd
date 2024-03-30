from datetime import datetime, timedelta
import connector
from ..const import const
from ..models.auth import Auth as auth


class Auth:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

        
    def login(self, manager_username: str, manager_password: str) -> bool:
        # Retrieve user data from the database by email
        manager_data = self.db.execute_query("SELECT manager_id, manager_password FROM tbl_manager WHERE manager_username = %s", (manager_username,))
        
        if manager_data:
            # Extract user_id and stored_password from the retrieved data
            manager_id, stored_password = manager_data[0]

            # Compare the hashed entered password with the stored password
            return auth.compare_passwords(manager_id, manager_password, stored_password)
        else:
            return False
        
    
    def change_password(self, manager_username, new_password, old_password):
        query = "SELECT manager_id, manager_password from tbl_manager WHERE manager_username = %s"
        value = (manager_username,)

        try:
            result = self.db.execute_query(query, value)
            manager_id, stored_password = result[0]

            if self.compare_passwords(manager_id, old_password, stored_password):
                return "Old password is incorrect", False
            
            new_password = self.encrypt_password(new_password, manager_id)

            query = "UPDATE tbl_manager SET password = %s WHERE manager_username = %s"
            values = (new_password, manager_username)

            self.db.execute_query(query, values)
            return "Update password successfully", True
        except Exception as e:
            print("Error changing password:", e)