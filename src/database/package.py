from . import connector

class Package:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

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