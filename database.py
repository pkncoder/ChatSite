import sqlite3

def createDatabase():
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS messages (
            messageID INTEGER PRIMARY KEY, 
            message TEXT, 
            timeSent TEXT,
            userID INTEGER,
            roomID INTEGER
        )
        ''')
    c.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            userID INTEGER PRIMARY KEY, 
            username TEXT,
            password TEXT,
            imagePath text,
            color TEXT
        )
        ''')
    c.execute(
        '''CREATE TABLE IF NOT EXISTS chatRooms (
            roomID INTEGER PRIMARY KEY,
            roomName TEXT
        )
        '''
    )
    c.execute(
        '''CREATE TABLE IF NOT EXISTS roomUser (
            roomID INTEGER,
            userID INTEGER,
            PRIMARY KEY (roomID, userID)
        )'''
    )
    conn.commit()
    conn.close()

def runCommand(command):
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()
    c.execute(command)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()
    c.execute("SELECT userID FROM users")

    for user in c.fetchall():
        c.execute("INSERT INTO roomUser VALUES (?, ?)", (1, user[0]))

    conn.commit()
    conn.close()