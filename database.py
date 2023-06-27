#!/Anaconda3/python
import psycopg2
from psycopg2.extras import RealDictCursor

from .logger import mylogger


class DataBase:
    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )

    def __str__(self):
        return f"<{self.__class__.__name__} : {self.host} : {self.port}>"

    def close(self):
        self.connection.close()

    def create_cursor(self):
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def close_cursor(self):
        self.cursor.close()

    def execute(self, sql, data, query=False):
        output = None
        self.create_cursor()
        try:
            self.cursor.execute(sql, data)
        except psycopg2.Error as e:
            mylogger.error(e.diag.message_primary)
            self.connection.rollback()

            return output
        if query:
            output=self.cursor.fetchall()
        else:
            self.connection.commit()
        self.close_cursor()
        
        return output

    def query(self, sql, data=None):
        output = self.execute(sql, data, query=True)

        return output

    def copy(self, data, table):
        output = None
        self.create_cursor()
        try:
            self.cursor.copy_from(data, table)
            self.connection.commit()
            output = 'OK'
        except psycopg2.Error as e:
            mylogger.error(e.diag.message_primary)
            self.connection.rollback()
        self.close_cursor()
        
        return output


def credential_db():
    import __auth__ as auth  # make this a hidden/untracked file
    host = auth.host
    port = auth.port
    username = auth.username
    password = auth.password
    database = auth.database

    return DataBase(host, port, username, password, database)


def connect_db():
    rv = credential_db()

    return rv


_connections = dict()

def get_db():
    if "db" not in _connections:
        _connections['db'] = connect_db()

    return _connections['db']


def refresh_request():
    request = get_db()
    
    return request
    
