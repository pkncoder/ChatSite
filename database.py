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
            roomName TEXT,
            isDM INTEGER
        )
        '''
    )
    c.execute(
        '''CREATE TABLE IF NOT EXISTS roomUser (
            roomID INTEGER PRIMARY KEY,
            userOneID INTEGER,
            userTwoID INTEGER
            PRIMARY KEY (roomID, userOneID, userTwo)
        )'''
    )
    conn.commit()
    conn.close()

def addAllDMs():
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()

    c.execute('SELECT userID, username FROM users')
    users = c.fetchall()

    for i in range(len(users)):
        for k in range(i, len(users)):
            if not i == k:

                c.execute('INSERT INTO chatRooms (roomName, isDM) VALUES (?, ?)', ("dmRoom", 1,))

                c.execute('SELECT roomID FROM chatRooms')
                currentID = c.fetchall()[-1][0]

                c.execute('INSERT INTO roomUser (roomID, userID) VALUES (?, ?)', (currentID, users[i][0],))
                c.execute('INSERT INTO roomUser (roomID, userID) VALUES (?, ?)', (currentID, users[k][0],))

    conn.commit()
    conn.close()

def deleteAllDMs():
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM chatRooms WHERE isDM = 1')

    c.execute('SELECT userID FROM users')
    users = c.fetchall()

    for user in users:

        c.execute('DELETE FROM roomUser WHERE userID = ?', (user[0],))

    conn.commit()
    conn.close()

def runCommand(command):
    conn = sqlite3.connect(f'databases/database.db')
    c = conn.cursor()
    c.execute(command)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # runCommand("ALTER TABLE chatRooms ADD isDM INTEGER")
    # runCommand("UPDATE chatRooms SET isDM = 0")
    deleteAllDMs()
    addAllDMs()