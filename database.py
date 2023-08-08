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
        self.db = sqlite3.connect('pyconnect.db')

    def create_struct(self) -> None:
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

        # create table last user used in application
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS last_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user VARCHAR(100),
                date DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        self.db.commit()

    def insert_user(self, server: str, user: str, password: str, server_cert: str) -> None:
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

    def select_user(self, user: str) -> list:
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

    def select_all_users(self) -> list:
        '''
        Select all users from database

        Returns:
            list: list of users
        '''
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT user FROM user;
        ''')
        return cursor.fetchall()

    def insert_last_user(self, user: str) -> None:
        '''
        Insert last user used in application

        Args:
            user (str): user name
        '''
        cursor = self.db.cursor()
        cursor.execute(f'''
            INSERT INTO last_user (user)
            VALUES ('{user}');
        ''')
        self.db.commit()

    def select_last_user(self) -> list:
        '''
        Select last user used in application

        Returns:
            list: list of users
        '''
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT user FROM last_user ORDER BY date DESC LIMIT 1;
        ''')
        return cursor.fetchall()
