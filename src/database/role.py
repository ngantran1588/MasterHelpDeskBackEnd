import re
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

    def generate_id(self) -> str:
        query = """SELECT MAX(role_id) FROM tbl_role"""
      
        result = self.db.execute_query(query)

        if result == None:
            return const.ROLE_ID_SUPER_USER

        last_id = result[0][0]  # Fetch the first element (the ID)

        # Extract the numeric part from the ID (assuming format "R" followed by digits)
        if last_id:
            match = re.search(r"R(\d{1,3})", last_id)  # Regex to extract up to 3 digits
            if match:
                numeric_part = int(match.group(1))
            else:
                raise ValueError("Invalid ID format encountered.")
        else:
            numeric_part = 0  # Start at 0 if no IDs exist

        # Generate the next ID with leading zeros for 3 digits
        next_id = f"R{numeric_part + 1:03d}"

        return next_id

    def add_role(self, role_name, description):

        role_id = self.generate_id()

        if role_id == None:
            return False
       
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