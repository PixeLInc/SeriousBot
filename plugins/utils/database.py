import psycopg2

class DatabaseException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Database:
    def __init__(self, user, password, dbname):
        self.username = user
        self.password = password
        self.db_name = dbname

        self.connection = None

    def connect(self):
        if self.connection is not None:
            return self.connection

        try:
            self.connection = psycopg2.connect(dbname=self.db_name, user=self.username, password=self.password, host='localhost')
        except psycopg2.Error as e:
            # 10/10 Error!
            raise DatabaseException(f"Failed to connect to database: {e.pgerror}")

        return self.connection

    def disconnect(self):
        if self.connection is None:
            return

        self.connection.close()

