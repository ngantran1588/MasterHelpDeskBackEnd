from . import connector
from datetime import datetime
from ..const import const
from ..models.auth import Auth as AuthAPI

class Package:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.auth = AuthAPI()

    def format_package_data(self, package_info):
        # Convert package information to key-value format
        return {
            "package_id": package_info[0],
            "package_name": package_info[1],
            "duration": package_info[2],
            "description": package_info[3],
            "slot_number": package_info[4],
            "slot_server": package_info[5],
            "price": package_info[6],
            "status": package_info[7]
        }

    def get_packages(self):
        query = "SELECT package_id,package_name,duration,description,slot_number,slot_server,price,status FROM tbl_package"

        try:
            result = self.db.execute_query(query)
            return [self.format_package_data(package) for package in result]
        except Exception as e:
            print("Error getting packages:", e)
            return None

    def get_package_by_id(self, package_id: str):
        query = "SELECT package_id,package_name,duration,description,slot_number,slot_server,price,status FROM tbl_package WHERE package_id = %s"
        value = (package_id,)
        try:
            result = self.db.execute_query(query, value)
            return self.format_package_data(result[0]) if result else None
        except Exception as e:
            print("Error getting package:", e)
            return None
        
    def add_package(self, package_name: str, duration: int, description: str, slot_number: int, slot_server: int, price: str, status: str):

        package_id = self.auth.generate_id(package_name)
        status = const.STATUS_ACTIVE

        query = """INSERT INTO tbl_package (package_id, package_name, duration, description, slot_number, slot_server, price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (package_id, package_name, duration, description, slot_number, slot_server, price, status)

        try:
            self.db.execute_query(query, values)
            print("Package added successfully!")
            return True
        except Exception as e:
            print("Error adding package:", e)
            return False
        
    def update_package(self, package_id: str, package_name: str, duration: datetime, description: str, slot_number: int, slot_server: int, price: str, status: str):
        query = """UPDATE tbl_package SET package_name = %s, duration = %s, description = %s, slot_number = %s, slot_server = %s, price = %s, status = %s WHERE package_id = %s"""
        values = (package_name, duration, description, slot_number, slot_server, price, status, package_id)

        try:
            self.db.execute_query(query, values)
            print("Package updated successfully!")
            return True
        except Exception as e:
            print(f"Error updating package with ID {package_id}:", e)
            return False
        
    def delete_package(self, package_id):
        query = """DELETE FROM tbl_package WHERE package_id = %s"""
        values = (package_id,)

        try:
            self.db.execute_query(query, values)
            print("Package deleted successfully!")
            return True
        except Exception as e:
            print(f"Error deleting package with ID {package_id}:", e)
            return False
        
    def get_package_by_amount(self, amount: str):
        query = "SELECT package_id,package_name,duration FROM tbl_package WHERE price = %s"
        value = (amount,)
        try:
            result = self.db.execute_query(query, value)
            data = None
            if result != None:
                package_info = result[0]
                data = {
                    "package_id": package_info[0],
                    "package_name": package_info[1],
                    "duration": package_info[2],
                }
            return data
        except Exception as e:
            print("Error getting package:", e)
            return None

    def get_number_package(self):     
        query = "SELECT COUNT(*) FROM tbl_package"
     
        try:
            result = self.db.execute_query(query)
            return result[0][0]
        except Exception as e:
            print("Error getting package number:", e)
            return False