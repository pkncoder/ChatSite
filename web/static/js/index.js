// Limit number for the amount of messages
// Starts at 15
let limitNum = 15;

// Connect to the socket on the server
const socket = io.connect(location.href);

// On document ready
$(document).ready(function() {
    // Settup the doc and call the function every minute
    setDoc();
});

// Update the messages
// Sent by the server
socket.on('update messages', function(msg){
    // Wait 2 seconds so the db can prossess the data
    // TODO: See if this can be made better
    sleep(3000).then(() => { setDoc(); });
})

// Send an event to the server that a message was sent
function ping() {

    // Emit a "ping" to the my event socet
    socket.emit("my event", "New Message Sent");
}

function changeServer(serverID) {
    document.cookie = `roomID = ${serverID};`
    location.reload();
}

// Settup the messages in the doc
function setDoc() {
    // Send ajax to get messages
    $.ajax({
        type: "GET",
        url: location.href + `getMessages/${getCookie('roomID')}?limitNum=` + limitNum, // Location plus getmessages with param of the limit num

        contentType: "application/json",

        // Success funcion
        success: function(response) {
            // Deal with all the messages coming in
            // Also check if anything was changed
            if (dealWithMessages(JSON.parse(response))) {

                // If it was, then move the scroll to the bottom
                let divElement = $('#messagesTop')[0];
                divElement.scrollTop = divElement.scrollHeight;
            }
        },

        // Error function
        error: function() {
            alert("ERROR");
        }
    });
};

// Deals with all the messages
function dealWithMessages(response) {

    // Get the messageContainer and reset the inside
    const messageContainer = $("#messagesContainer");
    messageContainer[0].innerHTML = "";

    // Loop every message in the response
    for (let messageIndex = 0; messageIndex < response.length; messageIndex++) {

        // Make a message div that is just html with the data from the message inside using the raw string
        let messageDiv = `
        <div class="container-fluid d-flex align-items-center gap-3 p-2 messageBox" id="${response[messageIndex][0]}">
            <img src="/static/${response[messageIndex][5]}" class="rounded-circle align-self-start mt-2" style="border: solid 2px {{ userData[3] }}; aspect-ratio: 1/1;" width="50" height="50">
            <div class="flex-grow-1" style="text-wrap: wrap;">
                <div>
                    <span style="color: ${response[messageIndex][4]}" class="h6">${response[messageIndex][3]}</span>
                    <span style="color: grey" class="h6">${response[messageIndex][2]}</span>
                </div>
                <span class="h2 h-100" style="color: ${response[messageIndex][4]}; overflow-wrap: anywhere;">${response[messageIndex][1]}</span>
            </div>
        `;

        if (`${response[messageIndex][6]}` === getCookie("userID")) {
            messageDiv += `<div class="rename" id="${response[messageIndex[0]]}">
                <button class="btn" onclick="editMessage('${response[messageIndex][0]}')"><i class="fa fa-refresh" style="font-size:48px;color:light-blue"></i></button>
            </div>`
        }

        if (getCookie("userID") == "1" || (`${response[messageIndex][6]}` === getCookie("userID"))) {
            messageDiv += `<div class="delete">
                <form action="/removeMessage/${response[messageIndex][0]}" method="get" onsubmit="ping()">
                    <button class="btn"><i class="fa fa-trash-o" style="font-size:48px;color:red"></i></button>
                </form>
            </div>`
        }

        messageDiv += "</div>"

        // Append the message to the message div
        messageContainer.append(messageDiv);
    }

    // Append a new button to the div to show more messages
    messageContainer.append(`<button id="moreMessagesButton" class="btn btn-sm btn-primary mb-2" style="width: 20%" onclick="moreMessages()">MORE MESSAGES</button>`);

    // If adding more is useless, then don't add anymore
    if (limitNum > $(".messageBox").length) {

        // Stop sending more requests by making the button disabled
        $("#moreMessagesButton")[0].className += " disabled";
    }

    // If anything was changed, then return true
    return true;
}

function editMessage(messageID) {
    div = $("#" + messageID)[0]

    div.innerHTML = `
    <form action="/editMessage/${messageID}" method="post" class="container w-100" onsubmit="ping()">
        <input class="form-control" name="text" type="text" placeholder="new text" required>
    </form>
    `
}

// Increase the message limit num and re-set the doc
function moreMessages() {
    limitNum += 15;
    setDoc();
}

// Sleep function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// W3schools
function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}