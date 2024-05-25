import unittest
from src.database.manager_auth import Auth
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):

    def test_login(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.login("julia", "123456")
        db.close()
        self.assertTrue(result)

    def test_change_password(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        _, result = auth.change_password("julia","1234567", "123456")
        db.close()
        self.assertTrue(result)

    def test_delete_user(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        _, result = auth.delete_user("hoangan12")
        db.close()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)