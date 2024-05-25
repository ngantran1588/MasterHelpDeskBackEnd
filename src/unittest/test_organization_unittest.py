import unittest
from src.database.organization import Organization
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):

    def test_add_organization(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Organization(db)

        result = auth.add_organization("Testing","0909311022","sirotroncut@gmail.com","Test ORG", "julia")
        db.close()
        self.assertTrue(result)
#chua xong
if __name__ == '__main__':
    unittest.main(verbosity=2)