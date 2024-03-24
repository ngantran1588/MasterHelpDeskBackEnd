from dotenv import load_dotenv
import os
load_dotenv()

class LoadDBEnv():
    def load_db_env():
        database_name = os.environ.get("DATABASE_NAME")
        database_user = os.environ.get("DATABASE_USER")
        database_pass = os.environ.get("DATABASE_PASS")
        database_host = os.environ.get("DATABASE_HOST")
        database_port = os.environ.get("DATABASE_PORT")

        db_env = [database_name, database_user, database_pass, database_host, database_port]

        return db_env

