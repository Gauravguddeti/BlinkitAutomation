#!/usr/bin/env python3
"""
send_email.py
Sends a plain-text email via Gmail SMTP using an App Password.
Credentials are read from environment variables — never from files.

Usage:
    python send_email.py <to_address_or_comma_list> <subject> <body_file_path>

    <to_address_or_comma_list> can be:
        - A single address:   "alice@gmail.com"
        - Multiple addresses: "alice@gmail.com,bob@gmail.com,carol@gmail.com"

Required environment variables:
    GMAIL_USER          Gmail address used as sender
    GMAIL_APP_PASSWORD  16-character App Password (spaces allowed, stripped automatically)

Exit codes: 0 = sent, 1 = error (message printed to stdout for PAD to capture)
"""

import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send(to_raw: str, subject: str, body: str) -> None:
    user = os.environ.get("GMAIL_USER", "").strip()
    password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")

    if not user or not password:
        raise RuntimeError(
            "GMAIL_USER or GMAIL_APP_PASSWORD is not set. "
            "Add them as Windows environment variables and restart PAD."
        )

    # Support comma-separated list of recipients
    recipients = [addr.strip() for addr in to_raw.split(",") if addr.strip()]
    if not recipients:
        raise RuntimeError("No valid recipient addresses provided.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(recipients)   # shows all in email header
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, recipients, msg.as_string())  # sends to all

    print(f"EMAIL_SENT=true TO={','.join(recipients)} COUNT={len(recipients)}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_email.py <to> <subject> <body_file>")
        sys.exit(1)

    to, subject, body_file = sys.argv[1], sys.argv[2], sys.argv[3]

    if not os.path.exists(body_file):
        print(f"ERROR: Body file not found: {body_file}")
        sys.exit(1)

    with open(body_file, encoding="utf-8") as f:
        body = f.read()

    try:
        send(to, subject, body)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
