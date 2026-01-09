# stt/merger.py

from typing import List, Dict
from pathlib import Path


def _find_speaker(start: float, end: float, diarization_segments: List[Dict]) -> str:
    for seg in diarization_segments:
        if max(start, seg["start"]) < min(end, seg["end"]):
            return seg["speaker"]
    return "UNKNOWN"


def _fill_unknown_speakers(segments: List[Dict]) -> List[Dict]:
    last_speaker = "UNKNOWN"
    for seg in segments:
        if seg["speaker"] == "UNKNOWN":
            seg["speaker"] = last_speaker
        else:
            last_speaker = seg["speaker"]
    return segments


def _merge_consecutive_segments(segments: List[Dict]) -> List[Dict]:
    merged = []

    for seg in segments:
        if not merged:
            merged.append(seg)
            continue

        last = merged[-1]
        if seg["speaker"] == last["speaker"]:
            last["end"] = seg["end"]
            last["text"] += " " + seg["text"]
        else:
            merged.append(seg)

    return merged


def _format_time(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def merge_transcript_and_speakers(
    whisper_segments: List[Dict],
    diarization_segments: List[Dict],
    save_path: str | None = None
) -> str:
    """
    Aligns Whisper transcript segments with diarization output.

    Returns:
        Speaker-attributed transcript (str)
    """
    # --- HARD VALIDATION ---
    if not whisper_segments:
        raise ValueError("whisper_segments is empty")

    if not isinstance(whisper_segments[0], dict):
        raise TypeError(
            "merge_transcript_and_speakers expects Whisper SEGMENTS, "
            "not plain text or list of strings.\n"
            "Pass result['segments'], not result['text']."
        )

    # Step 1: assign speaker to each whisper segment
    merged = []
    for w in whisper_segments:
        speaker = _find_speaker(w["start"], w["end"], diarization_segments)
        merged.append({
            "start": w["start"],
            "end": w["end"],
            "speaker": speaker,
            "text": w["text"].strip()
        })

    # Step 2: handle UNKNOWN speakers
    merged = _fill_unknown_speakers(merged)

    # Step 3: merge consecutive same-speaker segments
    merged = _merge_consecutive_segments(merged)

    # Step 4: build final transcript text
    lines = []
    for seg in merged:
        line = (
            f"[{_format_time(seg['start'])}–{_format_time(seg['end'])}] "
            f"{seg['speaker']}: {seg['text']}"
        )
        lines.append(line)

    final_text = "\n".join(lines)

    # Optional persistence
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(final_text, encoding="utf-8")

    return final_text
