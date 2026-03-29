!ffmpeg -i test_audio.mp3 -ar 16000 -ac 1 test.wav -y
!wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
!unzip -q vosk-model-small-en-us-0.15.zip

from vosk import Model, KaldiRecognizer
import wave, json

wf = wave.open("test.wav", "rb")
rec = KaldiRecognizer(Model("vosk-model-small-en-us-0.15"), 16000)

result = ""
while True:
    data = wf.readframes(4000)
    if not data:
        break
    if rec.AcceptWaveform(data):
        result += json.loads(rec.Result())["text"] + " "

result += json.loads(rec.FinalResult())["text"]
print("VOSK:", result)