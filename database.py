import sqlite3

class Databases:

    def __init__(self):
        createMessagesDatabase()
        createUsersDatabase()

def createMessagesDatabase():

    conn = sqlite3.connect(f'databases/messages.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY, 
            message TEXT, 
            username TEXT,
            color TEXT,
            timeSent TEXT
        )
        ''')
    conn.commit()
    conn.close()

def createUsersDatabase():

    conn = sqlite3.connect(f'databases/users.db')
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            favoriteColor TEXT NOT NULL
        )
        """)
    conn.commit()
    conn.close()
