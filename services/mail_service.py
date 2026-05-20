import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_email(to_email: str, subject: str, body: str):
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise ValueError("GMAIL_ADDRESS or GMAIL_APP_PASSWORD is not set in .env")

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = Header(subject, "utf-8")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [to_email], msg.as_string())