from flask import Flask, Response, make_response, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3

import datetime
import json
import os


"""
VARS
"""


# Flask app + create the socket
app = Flask(
    __name__,
    static_folder="web/static",
    template_folder="web/templates"
)
socket = SocketIO(app)


"""
SOCKETS
"""


# On the socket connected from client
@socket.on('connect')
def test_connect() -> None:
    emit('after connect',  {'data':'Connected'})

# Response from a client sending a new message
@socket.on('my event')
def handle_my_custom_event(message) -> None:

    # Send a command to update the messages to every client connected
    emit("update messages", message, broadcast=True)



@app.route('/')
def index() -> Response:

    if request.cookies.get('userID'):
       

        conn = sqlite3.connect('databases/database.db')
        c = conn.cursor()

        c.execute("SELECT username FROM users WHERE userID = ?", (request.cookies.get('userID'),))
        username = c.fetchall()[0][0]


        c.execute("SELECT roomID FROM roomUser WHERE userID = ?", (request.cookies.get('userID'),))

        dmList = []
        for room in c.fetchall():
            c.execute('''SELECT roomUser.roomID, chatRooms.isDM, users.userID, users.username 
                            FROM ((roomUser 
                                INNER JOIN users ON roomUser.userID = users.userID)
                                INNER JOIN chatRooms ON roomUser.roomID = chatRooms.roomID)
                            WHERE roomUser.roomID = ? AND chatRooms.isDM = 1 AND NOT roomUser.userID = ?;'''      
            , (room[0],request.cookies.get('userID'),))

            dmList += c.fetchall()

        c.execute('''SELECT chatRooms.roomID, chatRooms.roomName , roomUser.userID
                        FROM chatRooms
                            INNER JOIN roomUser ON chatRooms.roomID = roomUser.roomID
                        WHERE roomUser.userID = ? AND chatRooms.isDM = 0;''',
        (request.cookies.get('userID'),))
        roomList = c.fetchall()

        c.close()

        roomID = request.cookies.get('roomID')
        
        if not roomID:
            roomID = 1
            
        finalResponse = make_response(
            render_template('index.html', userID=request.cookies.get('userID'), username=username, roomList=roomList, dmList=dmList, roomID=roomID)
        )

        if not request.cookies.get('roomID'):
            finalResponse.set_cookie('roomID', "1")

        return finalResponse
    
    return redirect(url_for("loginSite"))

@app.route("/mananage")
def users() -> Response:
    if request.cookies.get('userID') == "1":
        conn = sqlite3.connect('databases/database.db')
        c = conn.cursor()

        c.execute('SELECT * FROM users')
        users = c.fetchall()

        c.execute('SELECT * FROM chatRooms WHERE isDM = 0')
        servers = c.fetchall()

        c.execute('''SELECT 
                roomUser.roomID, chatRooms.roomName, users.username, roomUser.userID
                  FROM ((roomUser
                  INNER JOIN chatRooms ON roomUser.roomID = chatRooms.roomID)
                  INNER JOIN users ON roomUser.userID = users.userID)
                  WHERE NOT roomName = "dmRoom"
                '''
        )
        userRoomCombos = c.fetchall()
        conn.close()

        return render_template("mananage.html", users=users, servers=servers, userRoomCombos=userRoomCombos)
    
    else:
        return redirect(url_for("index"))
    
@app.route('/removeRoom/<int:room_id>')
def delete_room(room_id) -> Response:
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute('DELETE FROM chatRooms WHERE roomID = ?', (room_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



@app.route("/addRoom", methods=["POST"])
def addRoom() -> Response:

    roomName = request.form["name"]

    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO chatRooms (roomName, isDM) VALUES (?,?)", (roomName,0,))
    conn.commit()
    conn.close()

    return redirect(url_for('users'))

@app.route('/addUserRoomCombo', methods=["POST"])
def addUserRoomCombo():

    roomID = request.form["roomID"]
    userID = request.form["userID"]

    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO roomUser (roomID, userID) VALUES (?, ?)", (roomID, userID))
    conn.commit()
    conn.close()

    return redirect(url_for('users'))

@app.route('/removeUserRoomCombo/<int:room_id>/<int:user_id>')
def delete_room_user(room_id, user_id) -> Response:
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute('DELETE FROM roomUser WHERE roomID = ? AND userID = ?', (room_id, user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('users'))

@app.route("/login")
def loginSite() -> Response:
    return render_template("login.html")

@app.route("/profile")
def profile() -> Response:
    userID = request.cookies.get('userID')

    if userID:

        conn = sqlite3.connect('databases/database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE userID = ?', (userID,))
        userData = c.fetchall()
        conn.close()

        return render_template('profile.html', userData=userData[0])
    
    return redirect(url_for("loginSite"))



@app.route('/sendMessage', methods=["POST"])
def sendMessage() -> Response:

    message = request.form['message']
    userID = request.form['userID']
    roomID = request.form['roomID']

    print(roomID)
    
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()

    time = datetime.datetime.now()

    c.execute('INSERT INTO messages (message, userID, timeSent, roomID) VALUES (?, ?, ?, ?)', (message, userID, time, roomID,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/removeMessage/<int:message_id>')
def delete_message(message_id) -> Response:
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE messageID = ?', (message_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



@app.route("/addUser", methods=["POST"])
def addUser() -> Response:

    username = request.form["username"]
    password = request.form["password"]
    favoriteColor = request.form["favoriteColor"]

    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, color) VALUES (?, ?, ?)", (username, password, favoriteColor))
    conn.commit()
    conn.close()

    return redirect(url_for('users'))

@app.route('/removeUser/<int:user_id>')
def delete_user(user_id) -> Response:
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE userID = ?', (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('users'))



# Check auth
@app.route('/auth', methods=["POST"])
def checkAuth() -> Response:

    # User username and password
    username = request.form['userUsername']
    password = request.form['userPassword']

    # Connect to the users database and get all the users from it (id,name,pass)
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute("SELECT userID, username, password FROM users")
    data = c.fetchall()
    conn.close()
    
    # Loop every suer
    for user in data:

        # If the username AND password is correct
        if user[1] == username:
            if user[2] == password:

                # Set the neccisarry cookies and return the final value
                return setAllSiteCookies(str(user[0]))
            
            # If the password is wrong for the unique user, break out of the loop
            else:
                break
    
    return "False"

# Sign's out a user (deletes all the cookies that the user id has)
@app.route('/signOut')
def signOut() -> Response:

    setAllSiteCookies("invalid", timeout=0)

    # Return the /login
    return redirect(url_for("loginSite"))

# Used to get messages, request arg: "limitNum" (the max number of messages to get)
@app.route("/getMessages/<int:roomID>", methods=["GET"])
def getMessages(roomID) -> str:
    
    # Connect to the database 
    conn = sqlite3.connect('databases/database.db')

    # Get the last messages sent, but only a spesific amount specified by request args
    c = conn.cursor()
    c.execute('SELECT messageID, message, timeSent, username, color, imagePath, messages.userID FROM messages INNER JOIN users on messages.userID = users.userID WHERE roomID = ? ORDER BY messageID DESC LIMIT ?', (roomID, request.args.get("limitNum"),))

    # Get a list of all the messages then close the database
    messages = c.fetchall()
    conn.close()
    
    # Return a string of all the messages
    return json.dumps(messages)

# Sets the site user id cookies
def setAllSiteCookies(value: str, timeout = None) -> Response:
    # /
    response = redirect(url_for('index'))
    response.set_cookie('userID', value, max_age=timeout)
    response.set_cookie('roomID', value, max_age=timeout)

    # /user
    userSite = redirect(url_for("users"))
    userSite.set_cookie('userID', value, max_age=timeout)
    userSite.set_cookie('roomID', value, max_age=timeout)

    # /profile
    profileSite = redirect(url_for("profile"))
    profileSite.set_cookie('userID', value, max_age=timeout)
    profileSite.set_cookie('roomID', value, max_age=timeout)

    return response

@app.route('/changeUserAccount', methods=["POST"])
def changeUserAccount() -> Response:

    # User username and password
    profilePictureFile = request.files['profilePicture']

    username = request.form['username']
    password = request.form['password']
    userID = request.form['userID']
    color = request.form['color']

    newPathFull = "web/static/assets/" + username + "." + profilePictureFile.filename.split(".")[-1].lower()
    newPathTable = "assets/" + username + "." + profilePictureFile.filename.split(".")[-1].lower()

    profilePictureFile.save(newPathFull)

    print(request.form['username'])

    # Connect to the users database and get all the users from it (id,name,pass)
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET userID = ?, username = ?, password = ?, color = ?, imagePath = ? WHERE userID = ?", (userID, username, password, color, newPathTable, userID,))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route('/editMessage/<int:message_id>', methods=["POST"])
def edit_message(message_id) -> Response:

    text = request.form["text"]

    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    c.execute('UPDATE messages SET message = ? WHERE messageID = ?', (text, message_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    socket.run(app, host='0.0.0.0', debug=True, port=5000)
