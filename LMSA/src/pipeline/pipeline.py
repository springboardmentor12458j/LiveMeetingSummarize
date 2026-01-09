from src.audio.system_audio_capture import record_audio
from src.stt.whisper_engine import transcribe_audio
from src.diarization.pyannote_diarizer import diarize_audio
from src.stt.merger import merge_transcript_and_speakers
from src.summarizer.groq_summarizer import summarize_text
from pathlib import Path


DATA_DIR = Path("data")

AUDIO_PATH = DATA_DIR / "audio" / "sample_audio.wav"
FINAL_TRANSCRIPT = DATA_DIR / "transcripts" / "final" / "speaker_transcript.txt"
SUMMARY_PATH = DATA_DIR / "summaries" / "meeting_summary.txt"


def run_pipeline(record_seconds: int = 60):

    print("Start recording")
    record_audio(str(AUDIO_PATH), record_seconds)
    print("end recording")

    print("Start transcripting")
    whisper_result = transcribe_audio(
        audio_path=str(AUDIO_PATH),
        save_text_path="data/transcripts/text/output.txt",
        save_json_path="data/transcripts/json/whisper.json"
    )
    print("end transcripting")

    print("start segmenting")
    speaker_segments = diarize_audio(
        audio_path=str(AUDIO_PATH),
        save_txt_path="data/diarization/diarization.txt"
    )
    print("end segmenting")

    print("start merging")
    final_text = merge_transcript_and_speakers(
        whisper_result["segments"],   # ✅ KEY FIX
        speaker_segments,
        save_path=str(FINAL_TRANSCRIPT)
    )
    print("end merging")

    print("start summarization")
    summary = summarize_text(
        whisper_result["text"],
        save_path=str(SUMMARY_PATH)
    )
    print("end summarization")

    return final_text, summary




def run_pipeline_from_audio(audio_path: str):
    """
    Pipeline that starts from an existing audio file
    (used by Streamlit / browser capture)
    """

    print("Start transcripting")
    whisper_result = transcribe_audio(
        audio_path=audio_path,
        save_text_path="data/transcripts/text/output.txt",
        save_json_path="data/transcripts/json/whisper.json"
    )
    print("end transcripting")

    print("start segmenting")
    speaker_segments = diarize_audio(
        audio_path=audio_path,
        save_txt_path="data/diarization/diarization.txt"
    )
    print("end segmenting")

    print("start merging")
    final_text = merge_transcript_and_speakers(
        whisper_result["segments"],
        speaker_segments,
        save_path=str(FINAL_TRANSCRIPT)
    )
    print("end merging")

    print("start summarization")
    summary = summarize_text(
        whisper_result["text"],
        save_path=str(SUMMARY_PATH)
    )
    print("end summarization")

    return final_text, summary
