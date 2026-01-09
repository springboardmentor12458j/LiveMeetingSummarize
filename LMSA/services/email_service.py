import smtplib
from email.message import EmailMessage
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_summary_email(receiver_email, summary_text):
    msg = EmailMessage()
    msg["Subject"] = "Meeting Summary"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg.set_content(summary_text)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
