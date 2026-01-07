import os
import whisper
import requests
import json
import setup_ffmpeg
import re
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
import nltk
import subprocess
import time
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Configuration ---
OLLAMA_EXE = r"C:\Users\alphi\AppData\Local\Programs\Ollama\ollama.exe"

# --- Configuration ---
# Configure FFmpeg path automatically
print("Configuring FFmpeg...")
ffmpeg_dir = setup_ffmpeg.check_and_install()
if ffmpeg_dir:
    os.environ["PATH"] += os.pathsep + ffmpeg_dir
    print(f"Added {ffmpeg_dir} to PATH.")
else:
    print("WARNING: FFmpeg setup failed. Audio processing may not work.")

UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Load Whisper Model ---
print("Loading Whisper model (base)... this may take a moment.")
audio_model = whisper.load_model("base")
print("Whisper model loaded.")

# --- Ollama Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi"

def generate_summary(transcript):
    """
    Sends the transcript to Ollama (phi model) to generate a structured summary.
    """
    prompt = f"""
    You are an expert meeting assistant. Please analyze the following meeting transcript and provide a structured output containing:
    1. **Summary**: A brief overview of the discussion.
    2. **Key Points**: Bullet points of important topics.
    3. **Action Items**: A list of tasks assigned or decided upon.

    Transcript:
    {transcript}
    """
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False 
    }
    
    try:
        # Check if Ollama is reachable; if not, suggest starting it
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=2) # Short timeout
        response.raise_for_status()
        return response.json().get('response', 'Error: No response from Ollama.')
    except requests.exceptions.RequestException:
        print("Ollama connection failed. Attempting to auto-start...")
        if start_ollama_server():
            # Retry once
            try:
                print("Retrying connection to Ollama...")
                response = requests.post(OLLAMA_API_URL, json=payload, timeout=10) # Longer timeout for first run
                response.raise_for_status()
                return response.json().get('response', 'Error: No response from Ollama.')
            except:
                pass
        
        print("Ollama still not reachable. Using fallback summarizer (Sumy).")
        return generate_fallback_summary(transcript)

def start_ollama_server():
    """Attempts to start 'ollama serve' in the background."""
    if not os.path.exists(OLLAMA_EXE):
        print(f"Ollama executable not found at {OLLAMA_EXE}")
        return False
    
    try:
        # Start Ollama in a separate process
        subprocess.Popen([OLLAMA_EXE, "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
        print("Starting Ollama... waiting 5 seconds.")
        time.sleep(5) # Give it time to spin up
        return True
    except Exception as e:
        print(f"Failed to auto-start Ollama: {e}")
        return False

def generate_fallback_summary(text):
    """
    Fallback summarization using Sumy (TextRank) and Regex for key points.
    Lightweight and works offline without Ollama.
    """
    if not text.strip():
        return "No text to summarize."

    # 1. Generate NLP Summary using TextRank
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    summary_sentences = summarizer(parser.document, 3) # Top 3 sentences
    
    summary_text = " ".join([str(s) for s in summary_sentences])

    # 2. Extract Key Points (Heuristic)
    # sentences containing keywords like "important", "key", "main"
    key_point_keywords = ["important", "crucial", "key", "main", "remember", "point"]
    sentences = text.split('.')
    key_points = []
    for s in sentences:
        if any(k in s.lower() for k in key_point_keywords):
            if len(s.strip()) > 10:
                key_points.append(f"- {s.strip()}")
    
    if not key_points:
        # If no keywords, just take the next best sentences from TextRank if available
        # Or just generic placeholder
        key_points = ["- (No specific key points detected automatically)"]

    # 3. Extract Action Items (Heuristic)
    # sentences containing "will", "going to", "task", "todo", "need to"
    action_keywords = ["will", "going to", "need to", "must", "assigned", "todo", "action"]
    action_items = []
    for s in sentences:
        if any(k in s.lower() for k in action_keywords):
             if len(s.strip()) > 10:
                action_items.append(f"- {s.strip()}")
    
    if not action_items:
        action_items = ["- (No specific action items detected automatically)"]

    return f"""**NOTE:** *Ollama was not reachable. This is a basic fallback summary.*

### Summary
{summary_text}

### Key Points
{chr(10).join(key_points)}

### Action Items
{chr(10).join(action_items)}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = os.path.join(UPLOAD_FOLDER, 'recording.webm')
        file.save(filename)
        print(f"Audio saved to {filename}")

        # 1. Transcribe
        try:
            print("Starting transcription...")
            # Force English for better accuracy and use valid FP32 if needed on CPU
            result = audio_model.transcribe(filename, language="English", fp16=False)
            transcript = result['text']
            print(f"Transcription complete: {transcript[:50]}...")
        except Exception as e:
            print(f"Transcription error: {e}")
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 500

        # 2. Summarize
        print("Starting summarization...")
        summary = generate_summary(transcript)
        print("Summarization complete.")

        return jsonify({
            'transcript': transcript,
            'summary': summary
        })

if __name__ == '__main__':
    # Run the app
    # host='0.0.0.0' allows access from local network (optional, but good for testing)
    app.run(debug=True, port=5000)
