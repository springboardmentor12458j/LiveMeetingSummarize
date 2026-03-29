!pip install sounddevice vosk faster-whisper soundfile
!apt-get install -y portaudio19-dev
from gtts import gTTS
from IPython.display import Audio

tts = gTTS("Hello, this is a test audio for speech to text models.", lang="en")
tts.save("test_audio.mp3")

Audio("test_audio.mp3")