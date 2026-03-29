# !pip install gTTS soundfile
from gtts import gTTS
import os

input_folder = "text_files"
output_folder = "audio_output"

os.makedirs(output_folder, exist_ok=True)

text_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]

for fname in text_files:
    file_path = os.path.join(input_folder, fname)

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if len(text) == 0:
        print(f"Skipping empty file: {fname}")
        continue

    tts = gTTS(text=text, lang="en")
    file_path = os.path.join(input_folder, fname)


    tts = gTTS(text=text, lang="en")

    base_name = os.path.splitext(fname)[0]
    output_path = os.path.join(output_folder, base_name + ".mp3")

    tts.save(output_path)
    print("Created:", output_path)

print("\n All text files converted to audio!")