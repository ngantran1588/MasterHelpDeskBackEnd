import unittest
from src.database.organization import Organization
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):

    def test_check_user_access(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.check_user_access("julia", "JzRCtRt6K1ax5ul4iqnNy6vM2NNzztEzf8W3rmYoxyE")
        db.close()
        self.assertTrue(result)

    def test_change_organization_status(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.change_organization_status( "JzRCtRt6K1ax5ul4iqnNy6vM2NNzztEzf8W3rmYoxyE", "INACTIVE")
        db.close()
        self.assertTrue(result)

    def test_update_information(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.update_information("Test","0909311022","hoanganngle2001@gmail.com", "Test unit", "JzRCtRt6K1ax5ul4iqnNy6vM2NNzztEzf8W3rmYoxyE")
        db.close()
        self.assertTrue(result)
    
    def test_add_user(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.add_user("JzRCtRt6K1ax5ul4iqnNy6vM2NNzztEzf8W3rmYoxyE", "henen")
        db.close()
        self.assertTrue(result)

    def test_check_organization_name_exist(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.check_organization_name_exist("Main Org")
        db.close()
        self.assertTrue(result)

    def test_get_remain_slot(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.get_remain_slot("julia")
        db.close()
        self.assertTrue(result)
        
    def test_delete_organization(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.delete_organization("JzRCtRt6K1ax5ul4iqnNy6vM2NNzztEzf8W3rmYoxyE")
        db.close()
        self.assertTrue(result)
if __name__ == '__main__':
    unittest.main(verbosity=2)