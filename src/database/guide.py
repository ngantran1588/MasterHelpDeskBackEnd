from datetime import datetime, timedelta
from . import connector
from ..const import const
from ..models.auth import Auth as AuthAPI

class Guide:
    def __init__(self, db: connector.DBConnector) -> None:
        self.db = db
        self.auth = AuthAPI()
        
    def get_guides(self):
        query = """SELECT guide_id,title,content FROM tbl_guide"""

        try:
            result = self.db.execute_query(query)
            print("Query guides successful!")
            if len(result) == 0:
                return None
            guides = []
            for guide_info in result:
                # Extract guides information and create a dictionary
                guide = {
                    "guide_id": guide_info[0],
                    "title": guide_info[1],
                    "content": guide_info[2]
                }
                guides.append(guide)

            return guides
        except Exception as e:
            print("Error querying guides:", e)

    def get_guide_by_id(self, guide_id):
        query = """SELECT title, content FROM tbl_guide WHERE guide_id = %s"""
        values = (guide_id,)

        try:
            result = self.db.execute_query(query, values)
            if len(result) == 0:
                return None
            guide_info = result[0]
            guide = {
                "guide_id": guide_id,
                "title": guide_info[0],
                "content": guide_info[1]
            }
            return guide
        except Exception as e:
            print(f"Error getting guide with ID {guide_id}:", e)

    def add_guide(self, title, content):

        guide_id = self.auth.generate_id(title)

        query = """INSERT INTO tbl_guide (guide_id, title, content) VALUES (%s, %s, %s)"""
        values = (guide_id, title, content)

        try:
            self.db.execute_query(query, values)
            print("Guide added successfully!")
            return True
        except Exception as e:
            print("Error adding guide:", e)
            return False

    def update_guide(self, guide_id, title, content):
        query = """UPDATE tbl_guide SET title = %s, content = %s WHERE guide_id = %s"""
        values = (title, content, guide_id)

        try:
            self.db.execute_query(query, values)
            print("Guide updated successfully!")
            return True
        except Exception as e:
            print(f"Error updating guide with ID {guide_id}:", e)
            return False

    def delete_guide(self, guide_id):
        query = """DELETE FROM tbl_guide WHERE guide_id = %s"""
        values = (guide_id,)

        try:
            self.db.execute_query(query, values)
            print("Guide deleted successfully!")
            return True
        except Exception as e:
            print(f"Error deleting guide with ID {guide_id}:", e)
            return False