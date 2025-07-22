function sendURL() {
    const url = document.getElementById("urlInput").value;

    fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url }),
    })
    .then(response => response.json())
    .then(data => {
        const output = document.getElementById("output");
        output.innerHTML = `<strong>${data.message}</strong><br><br><pre>${data.content || data.error}</pre>`;
    })
    .catch(error => {
        document.getElementById("output").innerText = "Error: " + error;
    });
}

function askQuestion() {
    const question = document.getElementById("questionInput").value;
    const context = document.getElementById("output").innerText;

    fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question, context: context }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("answer").innerText = data.answer || data.error;
    });
}

// 🎤 Optional: Voice Input (works only in Chrome)
function startVoiceInput() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("questionInput").value = transcript;
        askQuestion();  // auto-ask after voice input
    };

    recognition.start();
}
