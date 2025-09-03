
function analyzeComplaint() {
  const name = document.getElementById('name').value;
  const contact = document.getElementById('contact').value;
  const description = document.getElementById('description').value;

  if (!name || !contact || !description) {
    alert('Please fill in all fields before submitting.');
    return;
  }



  // Optional: send data to API
  /*
  fetch('https://your-api-endpoint.com/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, contact, description })
  })
  .then(res => res.json())
  .then(data => console.log('API response:', data))
  .catch(err => console.error('API error:', err));
  */
}

// === Voice Recognition Setup ===
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = true;
  recognition.interimResults = false;

  recognition.onresult = function (event) {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        transcript += event.results[i][0].transcript + ' ';
      }
    }
    document.getElementById('description').value += transcript;
  };

  recognition.onerror = function (event) {
    alert('Speech recognition error: ' + event.error);
  };

  document.getElementById('startBtn').addEventListener('click', () => {
    recognition.start();
    console.log('Voice input started');
  });

  document.getElementById('stopBtn').addEventListener('click', () => {
    recognition.stop();
    console.log('Voice input stopped temporarily');
  });

  document.getElementById('endBtn').addEventListener('click', () => {
    recognition.abort();
    console.log('Voice input ended');
  });

} else {
  alert("Sorry, your browser doesn't support Speech Recognition.");
}
