import psycopg2

class DBConnector:
    def __init__(self, dbname: str = None, user: str = None, password: str = None, host: str = None, port: int = None):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        try:
            # Connect to the PostgreSQL database
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Connected to the database")
        except psycopg2.Error as e:
            print("Error connecting to the database:", e)

    def close(self):
        # Close the database connection.
        if self.conn is not None:
            self.conn.close()
            print("Connection closed")