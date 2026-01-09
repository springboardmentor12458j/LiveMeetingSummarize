# stt/whisper_engine.py

import whisper
import os
import json
from pathlib import Path


# Cache model (huge performance win)
_MODEL_CACHE = {}


def _load_model(model_size: str):
    if model_size not in _MODEL_CACHE:
        print(f"Loading Whisper model [{model_size}]...")
        _MODEL_CACHE[model_size] = whisper.load_model(model_size)
    return _MODEL_CACHE[model_size]


def transcribe_audio(
    audio_path: str,
    save_text_path: str | None = None,
    save_json_path: str | None = None,
    model_size: str = "small"
) -> str:
    """
    Transcribes audio using OpenAI Whisper

    Returns:
        transcript text (str)
    """

    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = _load_model(model_size)

    print("Transcribing audio...")
    result = model.transcribe(str(audio_path))

    transcript_text = result["text"].strip()

    # Optional persistence (pipeline decides)
    if save_text_path:
        save_text_path = Path(save_text_path)
        save_text_path.parent.mkdir(parents=True, exist_ok=True)
        save_text_path.write_text(transcript_text, encoding="utf-8")

    if save_json_path:
        save_json_path = Path(save_json_path)
        save_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result
