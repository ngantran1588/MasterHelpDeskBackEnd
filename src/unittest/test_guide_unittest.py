import unittest
from src.database.guide import Guide
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):

    def test_add_guide(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Guide(db)

        result = auth.add_guide("Test case submit 1.0","Testing methods using python")
        db.close()
        self.assertTrue(result)

    def test_update_guide(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Guide(db)

        result = auth.update_guide("o8Tw9ojG0bslOSVOeOz8TVPyuW4JWRqv2tFvBGUWL0", "Test case submit 2.0","Python testing 2.0")
        db.close()
        self.assertTrue(result)

    def test_delete_guide(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Guide(db)

        result = auth.delete_guide("o8Tw9ojG0bslOSVOeOz8TVPyuW4JWRqv2tFvBGUWL0")
        db.close()
        self.assertTrue(result) 

if __name__ == '__main__':
    unittest.main(verbosity=2)