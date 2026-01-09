from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, flash, send_file, abort
)
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from flask import Blueprint

from src.pipeline.pipeline import run_pipeline_from_audio
from auth.auth_service import register_user, validate_user, user_exists
from services.email_service import send_summary_email
from utils.pdf_generator import generate_summary_pdf
from utils.text_cleaner import clean_markdown_text

# -------------------------------------------------
# ENV + APP SETUP
# -------------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "data" / "audio"
WEBM_PATH = AUDIO_DIR / "meeting.webm"
WAV_PATH  = AUDIO_DIR / "meeting.wav"

# -------------------------------------------------
# GLOBAL PROCESS STATUS (MVP SAFE)
# -------------------------------------------------
PROCESS_STATUS = {
    "state": "idle",        # idle | processing | completed
    "message": "Idle"
}

# -------------------------------------------------
# UTILS
# -------------------------------------------------
def normalize_speakers(text: str) -> str:
    speaker_map = {
        "SPEAKER_00": "Mentor",
        "SPEAKER_01": "Participant 1",
        "SPEAKER_02": "Participant 2",
    }
    for k, v in speaker_map.items():
        text = text.replace(k, v)
    return text

# -------------------------------------------------
# MAIN ROUTES
# -------------------------------------------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


@app.route("/status", methods=["GET"])
def status():
    return jsonify(PROCESS_STATUS)


@app.route("/upload", methods=["POST"])
def upload_audio():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    os.makedirs(AUDIO_DIR, exist_ok=True)

    PROCESS_STATUS["state"] = "processing"
    PROCESS_STATUS["message"] = "Processing audio… please wait"

    audio = request.files.get("audio")
    if not audio:
        return jsonify({"error": "No audio file"}), 400

    audio.save(WEBM_PATH)

    # Convert to WAV
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(WEBM_PATH),
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            str(WAV_PATH)
        ],
        capture_output=True
    )

    if not WAV_PATH.exists():
        PROCESS_STATUS["state"] = "idle"
        PROCESS_STATUS["message"] = "Audio conversion failed"
        return jsonify({"error": "WAV conversion failed"}), 500

    # Run pipeline
    transcript, summary = run_pipeline_from_audio(str(WAV_PATH))

    transcript = normalize_speakers(transcript)

    summary = summary.strip()
    if not summary.startswith("##"):
        summary = f"## **Meeting Summary**\n\n{summary}"

    # 🔑 STORE FOR PDF + EMAIL
    session["meeting_summary"] = summary

    PROCESS_STATUS["state"] = "completed"
    PROCESS_STATUS["message"] = "Processing completed"

    return jsonify({
        "transcript": transcript,
        "summary": summary
    })

# -------------------------------------------------
# AUTH ROUTES
# -------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if user_exists(email):
            return render_template("signup.html", error="User already exists")

        register_user(email, password)
        flash("Signup successful! Please login.", "success")
        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if validate_user(email, password):
            session["user"] = email
            PROCESS_STATUS["state"] = "idle"
            PROCESS_STATUS["message"] = "Idle"
            return redirect("/")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    PROCESS_STATUS["state"] = "idle"
    PROCESS_STATUS["message"] = "Idle"
    return redirect("/login")

# -------------------------------------------------
# EMAIL
# -------------------------------------------------
@app.route("/send-email", methods=["POST"])
def send_email():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    receiver = data.get("email")

    raw_summary = session.get("meeting_summary")
    if not receiver or not raw_summary:
        return jsonify({"error": "Invalid data"}), 400

    # ✅ CLEAN FOR EMAIL
    clean_summary = clean_markdown_text(raw_summary)

    send_summary_email(receiver, clean_summary)
    return jsonify({"status": "sent"})


# -------------------------------------------------
# PDF DOWNLOAD (BLUEPRINT)
# -------------------------------------------------
download_bp = Blueprint("download", __name__)

@download_bp.route("/download-summary", methods=["POST"])
def download_summary():
    summary = session.get("meeting_summary")

    if not summary:
        abort(400, "Summary not available")

    pdf_buffer = generate_summary_pdf(summary)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="meeting_summary.pdf",
        mimetype="application/pdf"
    )

# 🔑 REGISTER BLUEPRINT
app.register_blueprint(download_bp)

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
