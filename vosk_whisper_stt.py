!pip install -q vosk gTTS faster-whisper pydub soundfile sentencepiece
!apt -qq install -y ffmpeg

from google.colab import files
from gtts import gTTS
from IPython.display import Audio
import os, wave, json, subprocess

print("Upload audio (optional). Skip to auto-create TTS sample.")
up = files.upload()

if up:
    audio = list(up.keys())[0]
else:
    tts = gTTS("Hello! This is a test audio for comparing Vosk and Whisper.", lang="en")
    audio = "sample.mp3"
    tts.save(audio)


wav = "audio.wav"
subprocess.run(["ffmpeg","-y","-i",audio,"-ar","16000","-ac","1",wav],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if not os.path.exists("vosk-model"):
    !wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -O model.zip
    !unzip -q model.zip
    !mv vosk-model-small-en-us-0.15 vosk-model
    !rm model.zip

from vosk import Model, KaldiRecognizer

wf = wave.open(wav, "rb")
rec = KaldiRecognizer(Model("vosk-model"), wf.getframerate())
vosk_text = ""

while True:
    data = wf.readframes(4000)
    if not data:
        break

    if rec.AcceptWaveform(data):
        vosk_text += json.loads(rec.Result()).get("text", "") + " "
    else:
        vosk_text += json.loads(rec.FinalResult()).get("text", "") + " "

print("\n===== VOSK =====\n", vosk_text.strip())

import torch
from faster_whisper import WhisperModel

device = "cuda" if torch.cuda.is_available() else "cpu"
wmodel = WhisperModel("small", device=device)
segments, _ = wmodel.transcribe(wav)
whisper_text = " ".join([seg.text for seg in segments]).strip()
print("\n>>> WHISPER:\n", whisper_text)