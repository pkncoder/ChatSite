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
    sleep(2000).then(() => { setDoc(); });
})

// Send an event to the server that a message was sent
function ping() {

    // Emit a "ping" to the my event socet
    socket.emit("my event", "New Message Sent");
}

// Settup the messages in the doc
function setDoc() {
    // Send ajax to get messages
    $.ajax({
        type: "GET",
        url: location.href + 'getMessages?limitNum=' + limitNum, // Location plus getmessages with param of the limit num

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

    // If there aren't any new messages
    if (($(".messageBox").length <= 0) || (parseInt(response[response.length - 1][0]) !== parseInt($(".messageBox")[$(".messageBox").length - 1].id))) {

        // Get the messageContainer and reset the inside
        const messageContainer = $("#messagesContainer");
        messageContainer[0].innerHTML = "";

        // Loop every message in the response
        for (let messageIndex = 0; messageIndex < response.length; messageIndex++) {
            
            // Make a message div that is just html with the data from the message inside using the raw string
            const messageDiv = `
            <div class="container-fluid d-flex align-items-center gap-0 p-2 messageBox" id="${response[messageIndex][0]}">
                <div class="flex-grow-1" style="text-wrap: wrap;">
                    <div>
                        <span style="color: ${response[messageIndex][3]}" >${response[messageIndex][2]}</span>
                        <span style="color: grey">${response[messageIndex][4]}</span>
                    </div>
                    <p class="h4" style="color: ${response[messageIndex][3]}">${response[messageIndex][1]}</p>
                </div>
                <div class="delete">
                    <a href="/removeMessage/${response[messageIndex][0]}"><i class="fa fa-trash-o" style="font-size:48px;color:red"></i></a>
                </div>
            </div>
            `;

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

    // If nothing was changed, return false
    return false;
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