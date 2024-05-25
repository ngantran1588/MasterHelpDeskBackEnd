import unittest
from src.database.auth import Auth
from src.database import connector
from src.database.load_env import LoadDBEnv

class TestAuth(unittest.TestCase):
    def test_exist_username(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.exist_username("julia")
        db.close()
        self.assertTrue(result)

    def test_exist_email(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.exist_email("congchuadochoi@gmail.com")
        db.close()
        self.assertTrue(result)

    def test_login(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.login("julia", "123456")
        db.close()
        self.assertTrue(result)   
    
    def test_sign_up(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.sign_up("henen2", "123456", "EnNguyenn", "hoangan1@gmail.com")
        db.close()
        self.assertTrue(result)

    def test_change_role_to_superuser(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.change_role_to_superuser("henen")
        db.close()
        self.assertTrue(result)   
    
    def test_send_otp(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.send_otp("congchuadochoi@gmail.com")
        db.close()
        self.assertTrue(result)

    def test_verify_otp(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.verify_otp("congchuadochoi@gmail.com","733749")
        db.close()
        self.assertTrue(result)

    def test_delete_used_otp(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.delete_used_otp("congchuadochoi@gmail.com","733749")
        db.close()
        self.assertTrue(result)

    def test_change_password(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        _, result = auth.change_password("julia","12345678", "1234567")
        db.close()
        self.assertTrue(result)

    def test_reset_password(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        _, result = auth.reset_password("congchuadochoi@gmail.com","1234567")
        db.close()
        self.assertTrue(result)

    def test_get_user_name_from_email(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.get_username_from_email("congchuadochoi@gmail.com")
        db.close()
        self.assertEqual(result, "julia")

    def test_get_username_from_customer_id(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.get_username_from_customer_id("anVsaWFfMjAyNDAzMjMxNzI4MTM=")
        db.close()
        self.assertEqual(result, "julia")

    def test_get_email_from_username(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.get_email_from_username("henen")
        db.close()
        self.assertEqual(result, "congchuadochoi@gmail.com")

    def test_check_role(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.check_role("henen2")
        db.close()
        self.assertTrue(result)

    def test_check_user_pass(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.check_user_pass("julia","1234567")
        db.close()
        self.assertTrue(result)

    def test_update_information(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.update_information("julia","Julia", "congchuadochoi@gmail.com")
        db.close()
        self.assertTrue(result)

    def test_get_profile(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.get_profile("julia")
        db.close()
        self.assertEqual(result)
    
    def test_is_inactive_user(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        result = auth.is_inactive_user("henen")
        db.close()
        self.assertTrue(result)

    def test_change_status(self) -> bool:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        auth = Auth(db)

        _, result = auth.change_status("henen", "ACTIVE")
        db.close()
        self.assertTrue(result)

    
if __name__ == '__main__':
    unittest.main(verbosity=2)
    