import unittest
from src.database.package import Package
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):
    #Tested
    def test_add_package(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Package(db)

        result = auth.add_package("lamviec3", "2024-05-25 00:00:00", "jeje", "2", "2", "39.99", True)
        db.close()
        self.assertTrue(result)

    #Tested
    def test_update_package(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Package(db)

        result = auth.update_package("H1Hcx9XOazuIKCzwnoDC4Eq6SEh5dpR5OiSE7WTTOv0","lamviec2", "2024-05-26 00:00:00", "jejehehe", "3", "3", "49.99", True)
        db.close()
        self.assertTrue(result)

    #Tested
    def test_delete_package(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Package(db)

        result = auth.delete_package("H1Hcx9XOazuIKCzwnoDC4Eq6SEh5dpR5OiSE7WTTOv0")
        db.close()
        self.assertTrue(result)

    #Tested
    def test_get_number_package(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Package(db)

        result = auth.get_number_package()
        db.close()
        self.assertTrue(result)




    
if __name__ == '__main__':
    unittest.main(verbosity=2)