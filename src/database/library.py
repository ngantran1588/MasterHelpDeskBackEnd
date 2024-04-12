from . import connector
from ..const import const

class Library:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.db.connect()

    def insert_library(self, server_id: str, library: str, installed: bool):
        query = """INSERT INTO tbl_library (server_id, library, installed) VALUES (%s, %s, %s)"""
        values = (server_id, library, installed)

        try:
            self.db.execute_query(query, values)
            print("Library added successfully!")
            return True
        except Exception as e:
            print("Error adding library:", e)
            return False

    def update_library(self, server_id: str, library: str, installed: bool):
        query = """UPDATE tbl_library SET installed = %s WHERE server_id = %s AND library = %s"""
        values = (installed, server_id, library)

        try:
            self.db.execute_query(query, values)
            print("Library updated successfully!")
            return True
        except Exception as e:
            print(f"Error updating library with ID {server_id}:", e)
            return False
    
    def get_library(self, server_id: str, library: str):
        query = """SELECT installed FROM tbl_library WHERE server_id = %s AND library = %s"""
        values = (server_id, library,)

        try:
            result = self.db.execute_query(query, values)
            if len(result) == 0:
                return None
            library_info = result[0]
            library = {
                "server_id": server_id,
                "library": library,
                "installed": library_info[0]
            }
            return library
        except Exception as e:
            print(f"Error getting library with ID {server_id}:", e)
