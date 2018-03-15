import psycopg2
import psycopg2.extras

class DatabaseException(Exception):
    def __init__(self, message):
        super().__init__(message)

class Database:
    def __init__(self, user, password, dbname, host = 'localhost', port = 5432):
        self.username = user
        self.password = password
        self.db_name = dbname
        self.host = host
        self.port = port

        self.connection = None
        self.cursor = None

    def connect(self):
        if self.connection is not None:
            return self.connection

        try:
            self.connection = psycopg2.connect(dbname=self.db_name, user=self.username, password=self.password, host=self.host, port=self.port)
        except psycopg2.Error as e:
            raise DatabaseException(f"Failed to connect to database: {e}")

        return self.connection

    def is_connected(self):
        return self.connection is not None and self.connection.closed != 1

    def disconnect(self):
        if not self.is_connected():
            return

        self.connection.close()

    def _get_cursor(self):
        if not self.is_connected():
            raise DatabaseException("Tried to obtain a cursor while the database was closed!")

        if self.cursor is None or self.cursor.closed:
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

        return self.cursor

    def trivia_data(self, user_id = None, close = True):
        if not self.is_connected():
            return None

        cursor = self._get_cursor()

        # We want everything!
        if user_id is None:
            cursor.execute('SELECT * FROM trivia_data;')
            records = cursor.fetchall()
        else:
            # As per psycopg2's docs, You must either have a tuple with a trailing comma or a list as your passed in args
            cursor.execute('SELECT * FROM trivia_data WHERE user_id=%s', [user_id])
            records = cursor.fetchone()

        if close:
            cursor.close()

        return records


