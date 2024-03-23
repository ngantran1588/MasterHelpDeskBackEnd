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

    def execute_query(self, query, params=None):
        """
        Execute a query with optional parameters and return the result.
        """
        result = None
        try:
            # Create a cursor object
            cursor = self.conn.cursor()
            
            # Execute the query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch the result if any
            result = cursor.fetchall()
            
            # Commit the transaction (if needed)
            self.conn.commit()
        except psycopg2.Error as e:
            print("Error executing query:", e)
        finally:
            # Close the cursor
            if cursor:
                cursor.close()
        return result