let websocket;
let currentMessageId = null;
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const chatBody = document.getElementById("chat-body");
const sessionId = crypto.randomUUID();
const websocketURL = `ws://${window.location.host}/ws/${sessionId}`;
websocket = new WebSocket(websocketURL);

// Initialize WebSocket connection
function addWebSocketHandlers(ws) {
  ws.onopen = () => {
    console.log('WebSocket connected');
    // addSubmitHandler(ws);
    sendButton.addEventListener("click", function () {
      addSubmitHandler(ws);
    })
    userInput.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        addSubmitHandler(ws);
      }
    })
  };

  ws.onmessage = (event) => {
    const packet = JSON.parse(event.data);

    if (packet.turn_complete && packet.turn_complete == true) {
      currentMessageId = null;
      return;
    }

    if (currentMessageId == null) {
      currentMessageId = crypto.randomUUID();
      const message = document.createElement("div");
      message.id = currentMessageId;
      message.classList.add("agent-message");
      chatBody.appendChild(message);
    }

    const message = document.getElementById(currentMessageId);
    message.textContent += packet.message;
    chatBody.scrollTop = chatBody.scrollHeight; // Scroll to bottom
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
    //Try to reconnect
    setTimeout(function() {
      console.log("Websocket Reconnecting...")
      ws = new WebSocket(websocketURL);
      addWebSocketHandlers(ws);
    }, 5000)
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
}

addWebSocketHandlers(websocket);

function addSubmitHandler(ws) {
  const message = userInput.value.trim();
  if (message) {
    const div = document.createElement("div");
    div.classList.add("user-message");
    div.textContent = message;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
    ws.send(message);
    console.log(message);
    userInput.value = "";
  }
  return false;
}
