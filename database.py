import sqlite3

def createDatabase():
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS messages (
            messageID INTEGER PRIMARY KEY, 
            message TEXT, 
            userID INTEGER,
            timeSent TEXT
        )
        ''')
    c.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            userID INTEGER PRIMARY KEY, 
            usernamme TEXT, 
            password TEXT,
            color TEXT
        )
        ''')
    conn.commit()
    conn.close()

def runCommand(command):
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()
    c.execute(command)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    runCommand("ALTER TABLE messages ADD timeSent TEXT")
    runCommand("ALTER TABLE users RENAME COLUMN usernamme TO username")