const chatLog = document.getElementById('chat-log');
const recordButton = document.getElementById('record-button');
const stopButton = document.getElementById('stop-button');

let websocket;
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let currentMessageId = null;
const sessionId = crypto.randomUUID();
const websocketURL = `ws://${window.location.host}/ws/${sessionId}`;
websocket = new WebSocket(websocketURL);

// Initialize WebSocket connection
function addWebSocketHandlers(ws) {
  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onmessage = (event) => {
    const packet = JSON.parse(event.data);

    if (packet.turn_complete == true) {
      currentMessageId = null;
      return;
    }

    if (currentMessageId == null) {
      currentMessageId = crypto.randomUUID();
      const message = document.createElement("p");
      message.id = currentMessageId;
      chatLog.appendChild(message);
    }

    const message = document.getElementById(currentMessageId);
    message.textContent += packet.message;
    chatLog.scrollTop = chatLog.scrollHeight; // Scroll to bottom
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

function sendAudioData(chunk) {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(chunk);
    console.log(chunk);
  } else {
    console.warn("WebSocket not connected. Audio chunk dropped.");
  }
}

recordButton.addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
      sendAudioData(event.data); // Send each chunk to WebSocket server
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      console.log("Recording stopped, audio blob size:", audioBlob.size);
      // Optional:  Process or download the audio blob here.
      // const audioURL = URL.createObjectURL(audioBlob);
      // const a = document.createElement('a');
      // a.href = audioURL;
      // a.download = 'recording.webm';
      // a.click();
      // URL.revokeObjectURL(audioURL);

      // Reset button states
      recordButton.disabled = false;
      stopButton.disabled = true;
    };

    mediaRecorder.start();
    recordButton.disabled = true;
    stopButton.disabled = false;
    console.log('Recording started');

  } catch (err) {
    console.error('Error getting microphone permission:', err);
  }
});

stopButton.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    console.log('Recording stopped (stop button)');
    websocket.send('<audio complete>')
  } else {
    console.warn("MediaRecorder not initialized or not recording.");
  }
});
