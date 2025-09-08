from smtplib import SMTP, SMTP_SSL
from email.message import EmailMessage
import os
# https://forum-raspberrypi.de/forum/thread/57219-e-mail-mit-gmx-versenden/

def send_email(
    msg_text: str,
    msg_from: str,
    msg_to: str | list[str],
    password: str,
    host: str,
    port: int,
    username: str | None = None,
    msg_subject: str = "",
    starttls: bool = False,
    explicit_tls: bool = False,
):
    if starttls and explicit_tls:
        raise ValueError("`starttls` and `explicit_tls` are mutally exclusive")

    if isinstance(msg_to, str):
        msg_to = [msg_to]

    if username is None:
        username = msg_from

    msg = EmailMessage()
    msg["From"] = msg_from
    msg["To"] = " ".join(msg_to)
    msg["Subject"] = msg_subject
    msg.set_content(msg_text)

    if starttls:
        smtp = SMTP(host, port)
    elif explicit_tls:
        smtp = SMTP_SSL(host, port)
    else:
        smtp = SMTP(host, port)

    with smtp:
        smtp.ehlo()

        if starttls:
            smtp.starttls()

        smtp.login(username, password)
        smtp.send_message(msg)


def main():
    from dotenv import load_dotenv
    # use this to debug
    load_dotenv()

    msg_subject = "Test message"
    msg_text = "hello\n"

    msg_from = os.getenv("EMAIL_FROM")
    msg_to = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_APP_SPECIFIC_PW")
    host = os.getenv("EMAIL_HOST")
    port = os.getenv("EMAIL_PORT")
    port = int(port)

    username = os.getenv("EMAIL_USER")

    if None in [msg_from, msg_to, password, host, port]:
        raise ValueError

    send_email(host=host,
               port=port,
               starttls=True,
               msg_from=msg_from,
               msg_to=msg_to,
               password=password,
               msg_text=msg_text,
               msg_subject=msg_subject
               )

if __name__ == "__main__":
    main()
