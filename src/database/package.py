from . import connector

class Package:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

    def get_packages(self):
        query = "SELECT * FROM tbl_package"

        try:
            result = self.db.execute_query(query)
            return result
        except Exception as e:
            print("Error getting organization number of members:", e)
            return None

    def get_package_by_id(self, package_id: str):
        query = "SELECT * FROM tbl_package WHERE package_id = %s"
        value = (package_id,)
        try:
            result = self.db.execute_query(query, value)
            return result
        except Exception as e:
            print("Error getting organization number of members:", e)
            return None