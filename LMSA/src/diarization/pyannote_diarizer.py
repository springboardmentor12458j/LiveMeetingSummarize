import os
from pathlib import Path
from pyannote.audio import Pipeline
from dotenv import load_dotenv

load_dotenv()

# Model cache (critical for performance)
_PIPELINE_CACHE = {}

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = "pyannote/speaker-diarization"


def _load_pipeline():
    if MODEL_NAME not in _PIPELINE_CACHE:
        if not HF_TOKEN:
            raise EnvironmentError(
                "HF_TOKEN not set. Please add it to your environment variables."
            )

        print("Loading PyAnnote diarization pipeline...")
        _PIPELINE_CACHE[MODEL_NAME] = Pipeline.from_pretrained(
            MODEL_NAME,
            use_auth_token=HF_TOKEN
        )

    return _PIPELINE_CACHE[MODEL_NAME]


def diarize_audio(
    audio_path: str,
    save_txt_path: str | None = None
) -> list[dict]:
    """
    Performs speaker diarization.

    Returns:
        List of segments:
        [
            {
                "start": float,
                "end": float,
                "speaker": str
            }
        ]
    """

    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    pipeline = _load_pipeline()

    print("Running speaker diarization...")
    diarization = pipeline(str(audio_path))

    segments = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
            "speaker": speaker
        })

    # Optional persistence (pipeline decides)
    if save_txt_path:
        save_txt_path = Path(save_txt_path)
        save_txt_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_txt_path, "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(
                    f"{seg['start']}s - {seg['end']}s | Speaker {seg['speaker']}\n"
                )

    return segments
