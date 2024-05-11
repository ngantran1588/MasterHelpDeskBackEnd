from datetime import datetime, timedelta
from . import connector
from ..const import const
from ..models.auth import Auth as AuthAPI

class Role:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.auth = AuthAPI()
        
    def get_roles(self):
        query = """SELECT role_id,role_name,description FROM tbl_role"""

        try:
            result = self.db.execute_query(query)
            print("Query roles successful!")
            if len(result) == 0:
                return None
            roles = []
            for role_info in result:
                # Extract roles information and create a dictionary
                role = {
                    "role_id": role_info[0],
                    "role_name": role_info[1],
                    "description": role_info[2]
                }
                roles.append(role)

            return roles
        except Exception as e:
            print("Error querying roles:", e)

    def get_role_by_id(self, role_id):
        query = """SELECT role_name, description FROM tbl_role WHERE role_id = %s"""
        values = (role_id,)

        try:
            result = self.db.execute_query(query, values)
            if len(result) == 0:
                return None
            role_info = result[0]
            role = {
                "role_id": role_id,
                "role_name": role_info[0],
                "description": role_info[1]
            }
            return role
        except Exception as e:
            print(f"Error getting role with ID {role_id}:", e)

    def add_role(self, role_name, description):

        role_id = self.auth.generate_id(role_name)

        query = """INSERT INTO tbl_role (role_id, role_name, description) VALUES (%s, %s, %s)"""
        values = (role_id, role_name, description)

        try:
            self.db.execute_query(query, values)
            print("role added successfully!")
            return True
        except Exception as e:
            print("Error adding role:", e)
            return False

    def update_role(self, role_id, role_name, description):
        query = """UPDATE tbl_role SET role_name = %s, description = %s WHERE role_id = %s"""
        values = (role_name, description, role_id)

        try:
            self.db.execute_query(query, values)
            print("role updated successfully!")
            return True
        except Exception as e:
            print(f"Error updating role with ID {role_id}:", e)
            return False

    def delete_role(self, role_id):
        query = """DELETE FROM tbl_role WHERE role_id = %s"""
        values = (role_id,)

        try:
            self.db.execute_query(query, values)
            print("role deleted successfully!")
            return True
        except Exception as e:
            print(f"Error deleting role with ID {role_id}:", e)
            return False