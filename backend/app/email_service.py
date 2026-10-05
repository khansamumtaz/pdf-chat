import smtplib
from email.message import EmailMessage
from .config import settings

def send_email(to: str, subject: str, body: str):
    if not settings.SMTP_USER or not settings.SMTP_APP_PASSWORD:
        raise RuntimeError("SMTP is not configured")
    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_APP_PASSWORD)
        server.send_message(msg)

def send_otp_email(to: str, otp: str, purpose: str):
    body = (
        f"Your OTP to {purpose} is: {otp}\n\n"
        f"It expires in {settings.OTP_EXPIRE_MINUTES} minutes. "
        "If you did not request this, ignore this email."
    )
    send_email(to, "Your AI PDF Chat OTP", body)