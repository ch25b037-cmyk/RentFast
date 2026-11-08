"""Minimal console/SMTP mail boundary used by passwordless authentication."""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger("campuslend.mail")


def deliver_otp(email: str, code: str) -> None:
    settings = get_settings()
    if settings.mail_backend == "console":
        logger.info("[console mail] OTP for %s: %s", email, code)
        return
    if settings.mail_backend != "smtp" or not settings.smtp_host:
        raise RuntimeError("SMTP mail is not configured.")

    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = email
    message["Subject"] = "Your CampusLend sign-in code"
    message.set_content(f"Your CampusLend sign-in code is {code}. It expires in {settings.otp_ttl_minutes} minutes.")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        if settings.smtp_starttls:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)
