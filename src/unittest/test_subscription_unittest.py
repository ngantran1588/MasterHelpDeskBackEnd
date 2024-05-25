import unittest
from src.database.subscription import Subscription
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):

    def test_check_subscription_by_username(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Subscription(db)

        result = auth.check_subscription_by_username("julia")
        db.close()
        self.assertTrue(result)

    def test_add_subscription(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Subscription(db)

        result = auth.add_subscription("conmeno","anVsaWFfMjAyNDAzMjMxNzI4MTM=","overrated", "2024-05-27 00:00:00", True )
        db.close()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)