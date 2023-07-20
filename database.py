import sqlite3
import os


class Database():
    '''
    Database class
    '''
    def __init__(self) -> None:
        '''
        Constructor to init database
        '''
        self.db = sqlite3.connect(f'{os.environ.get("HOME")}/.local/bin/pyconnect_utils/pyconnect.db')

    def create_struct(self):
        '''
        Create database structure
        '''
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server VARCHAR(100),
                user VARCHAR(100),
                password VARCHAR(100),
                server_cert VARCHAR(100)
            );
        ''')

        self.db.commit()

    def insert(self, server: str, user: str, password: str, server_cert: str):
        '''
        Insert new user in database

        Args:
            server (str): server name
            user (str): user name
            password (str): user password
            server_cert (str): server certificate
        '''
        cursor = self.db.cursor()
        cursor.execute(f'''
            INSERT INTO user (server, user, password, server_cert)
            VALUES ('{server}', '{user}', '{password}', '{server_cert}');
        ''')
        self.db.commit()

    def select(self, user: str) -> list:
        '''
        Select user from database

        Args:
            user (str): user name

        Returns:
            list: list of users
        '''
        cursor = self.db.cursor()
        cursor.execute(f'''
            SELECT server, server_cert, user, password FROM user WHERE user = '{user}';
        ''')
        return cursor.fetchall()

    def select_all(self) -> list:
        '''
        Select all users from database

        Returns:
            list: list of users
        '''
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT server, server_cert, user, password FROM user;
        ''')
        return cursor.fetchall()
