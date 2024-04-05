from . import connector

class Package:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

    def format_package_data(self, package_info):
        # Convert package information to key-value format
        return {
            "package_id": package_info["package_id"],
            "package_name": package_info["package_name"],
            "duration": package_info["duration"],
            "description": package_info["description"],
            "slot_number": package_info["slot_number"],
            "slot_server": package_info["slot_server"],
            "price": package_info["price"],
            "status": package_info["status"]
        }

    def get_packages(self):
        query = "SELECT * FROM tbl_package"

        try:
            result = self.db.execute_query(query)
            return [self.format_package_data(package) for package in result]
        except Exception as e:
            print("Error getting organization number of members:", e)
            return None

    def get_package_by_id(self, package_id: str):
        query = "SELECT * FROM tbl_package WHERE package_id = %s"
        value = (package_id,)
        try:
            result = self.db.execute_query(query, value)
            return self.format_package_data(result[0]) if result else None
        except Exception as e:
            print("Error getting organization number of members:", e)
            return None