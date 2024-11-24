from flask import Flask, Response, make_response, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3

import json
import datetime

from database import Databases


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
        
        return make_response(
            render_template('index.html', userID=request.cookies.get('userID'))
        )
    
    return redirect(url_for("loginSite"))

@app.route("/users")
def users() -> Response:
    if request.cookies.get('userID') == "1":
        conn = sqlite3.connect('databases/users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        conn.close()

        return render_template("users.html", users=users)
    
    else:
        return redirect(url_for("index"))

@app.route("/login")
def loginSite() -> Response:
    return render_template("login.html")

@app.route("/profile")
def profile() -> Response:
    userID = request.cookies.get('userID')

    if userID:

        conn = sqlite3.connect('databases/users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (userID,))
        userData = c.fetchall()
        conn.close()

        return render_template('profile.html', userData=userData[0])
    
    return redirect(url_for("loginSite"))



@app.route('/sendMessage', methods=["POST"])
def sendMessage() -> Response:

    message = request.form['message']
    userID = request.form['userID']
    
    conn = sqlite3.connect('databases/users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (userID,))
    data = c.fetchall()
    conn.close()

    username = data[0][1]
    color = data[0][3]
    time = datetime.datetime.now()

    conn = sqlite3.connect('databases/messages.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (message, username, color, timeSent) VALUES (?, ?, ?, ?)', (message, username, color, time))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/removeMessage/<int:message_id>')
def delete_message(message_id) -> Response:
    conn = sqlite3.connect('databases/messages.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))



@app.route("/addUser", methods=["POST"])
def addUser() -> Response:

    username = request.form["username"]
    password = request.form["password"]
    favoriteColor = request.form["favoriteColor"]

    conn = sqlite3.connect('databases/users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, favoriteColor) VALUES (?, ?, ?)", (username, password, favoriteColor))
    conn.commit()
    conn.close()

    return redirect(url_for('users'))

@app.route('/removeUser/<int:user_id>')
def delete_user(user_id) -> Response:
    conn = sqlite3.connect('databases/users.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
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
    conn = sqlite3.connect('databases/users.db')
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users")
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
@app.route("/getMessages", methods=["GET"])
def getMessages() -> str:
    
    # Connect to the database 
    conn = sqlite3.connect('databases/messages.db')

    # Get the last messages sent, but only a spesific amount specified by request args
    c = conn.cursor()
    c.execute('SELECT * FROM messages ORDER BY id DESC LIMIT ?', (request.args.get("limitNum"),))

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

    # /user
    userSite = redirect(url_for("users"))
    userSite.set_cookie('userID', value, max_age=timeout)

    # /profile
    profileSite = redirect(url_for("profile"))
    profileSite.set_cookie('userID', value, max_age=timeout)

    return response

@app.route('/changeUserAccount', methods=["POST"])
def changeUserAccount() -> Response:

    # User username and password
    username = request.form['username']
    password = request.form['password']
    userID = request.form['userID']
    color = request.form['color']

    # Connect to the users database and get all the users from it (id,name,pass)
    conn = sqlite3.connect('databases/users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET id = ?, username = ?, password = ?, favoriteColor = ? WHERE id = ?", (userID, username, password, color, userID,))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

if __name__ == '__main__':
    Databases()

    
    # app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000, debug=True)
    socket.run(app, host='0.0.0.0', debug=True, port=5000)
