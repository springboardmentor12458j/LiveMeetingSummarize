# Live Meeting Summarizer

A local, offline-capable application that records audio, transcribes it using OpenAI Whisper, and generates a structured summary using Ollama (Phi model).

## Prerequisites

1.  **Anaconda (or Miniconda)** installed on Windows.
2.  **Ollama** installed and running. [Download Ollama](https://ollama.com/)
3.  **FFmpeg** (Handled Automatically).
    -   The application will automatically download and configure FFmpeg on the first run.
    -   No manual installation required!

## Setup Instructions

1.  **Open "Anaconda Prompt"**.

2.  **Navigate to the project folder:**
    ```cmd
    cd "D:\live meaing summarizer"
    ```

3.  **Create a new environment (optional but recommended):**
    ```cmd
    conda create -n summarizer python=3.9
    conda activate summarizer
    ```

4.  **Install Dependencies:**
    ```cmd
    pip install -r requirements.txt
    ```
    *Note: If you get an error about 'ffmpeg', run `conda install -c conda-forge ffmpeg`.*

5.  **Prepare Ollama:**
    Open a *separate* terminal (Command Prompt or PowerShell) and run:
    ```cmd
    ollama pull phi
    ollama serve
    ```
    *Keep this terminal open.*

## Running the Application

1.  In your Anaconda Prompt (where you installed pip requirements), run:
    ```cmd
    python app.py
    ```

2.  Wait for the message: `Whisper model loaded.` (The first run will download the model, which may take a minute).

3.  Open your browser and go to:
    [http://localhost:5000](http://localhost:5000)

4.  **How to use:**
    -   Click **Start Recording**.
    -   Speak into your microphone.
    -   Click **Stop & Process**.
    -   Wait for the processing to finish (transcription + summarization).
    -   View your Transcript and Summary!
