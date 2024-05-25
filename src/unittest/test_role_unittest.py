import unittest
from src.database.role import Role
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):

    def test_add_role(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Role(db)

        result = auth.add_role( "Cuutoi", "tester enen 2.0")
        db.close()
        self.assertTrue(result)

    def test_update_role(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Role(db)

        result = auth.update_role("R003", "Whatthefuckisthis", "tester enen")
        db.close()
        self.assertTrue(result)

    def test_delete_role(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Role(db)

        result = auth.delete_role("R003")
        db.close()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)