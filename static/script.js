let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById('recordBtn');
const stopBtn = document.getElementById('stopBtn');
const statusDiv = document.getElementById('status');
const resultsContainer = document.getElementById('results');
const transcriptOutput = document.getElementById('transcriptOutput');
const summaryOutput = document.getElementById('summaryOutput');

recordBtn.addEventListener('click', startRecording);
stopBtn.addEventListener('click', stopRecording);

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = sendAudioData;

        mediaRecorder.start();
        
        // UI Updates
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        statusDiv.textContent = "Recording in progress...";
        statusDiv.classList.add('recording-pulse');
        resultsContainer.classList.add('hidden'); // Hide previous results
    } catch (err) {
        console.error("Error accessing microphone:", err);
        statusDiv.textContent = "Error: Could not access microphone. Please allow permissions.";
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        // Stop all tracks to release microphone
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // UI Updates
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        statusDiv.classList.remove('recording-pulse');
        statusDiv.textContent = "Processing audio... This may take a moment.";
    }
}

async function sendAudioData() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
        const response = await fetch('/process_audio', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || `Server error: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);

    } catch (err) {
        console.error("Error sending audio:", err);
        statusDiv.textContent = `Error: ${err.message}`;
    }
}

function displayResults(data) {
    statusDiv.textContent = "Processing complete!";
    
    // Display Transcript
    transcriptOutput.textContent = data.transcript;

    // Display Summary (Handle newlines/markdown-ish text simply)
    // We can use a simple replace for newlines to <br> for better basic rendering
    // or just rely on CSS white-space: pre-wrap.
    summaryOutput.innerText = data.summary; // innerText preserves newlines

    resultsContainer.classList.remove('hidden');
}
