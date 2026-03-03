import imaplib
import email
from email.header import decode_header
from datetime import datetime
import ssl
import json


def decode_mime_words(s):
    if not s:
        return ""
    decoded_fragments = decode_header(s)
    return "".join(
        fragment.decode(encoding or "utf-8") if isinstance(fragment, bytes) else fragment
        for fragment, encoding in decoded_fragments
    )


def extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore")

    return ""


def fetch_todays_emails(config):
    context = ssl.create_default_context()

    mail = imaplib.IMAP4_SSL(
        config.IMAP_SERVER,
        config.IMAP_PORT,
        ssl_context=context
    )

    mail.login(config.EMAIL_ACCOUNT, config.EMAIL_PASSWORD)
    mail.select(config.MAILBOX)

    today = datetime.today().strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'(ON "{today}")')

    email_list = []

    if status == "OK":
        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            email_data = {
                "id": num.decode(),
                "date": msg.get("Date"),
                "from": decode_mime_words(msg.get("From")),
                "subject": decode_mime_words(msg.get("Subject")),
                "body": extract_body(msg)
            }

            email_list.append(email_data)

    mail.logout()
    return email_list


def save_to_json(data, path="data/raw_mails.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)