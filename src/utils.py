import os
from time import sleep
from typing import Callable, Any

from send_mail import send_email


def silencer(func: Callable[..., Any], b: bool) -> Callable[..., Any]:
    """

    :param func: buzzer function
    :param b: bool indicating if funcis supposed to be executed
    :return: wrapper that only executes func if b is False
    """
    def wrapper(*args, **kwargs) -> None:
        if not b:
            func(*args, **kwargs)
    return wrapper


def beeper(on: Callable[..., Any], off: Callable[..., Any]) -> Callable[..., Any]:
    """

    :param on: a function activating something
    :param off: a function deactivatinga something
    :return: a function toggling something
    """
    def beeper_wrapper(beeps:int=1, t:int=0.2) -> None:
        for i in range(beeps):
            on()
            sleep(t)
            off()
            if i!=beeps-1:
                sleep(t)
    return beeper_wrapper


class LogEntry:
    def __init__(self, label : str, value : Any, unit : str = None) -> None :
        self.label = label
        self.value = value
        self.unit = unit

    def __str__(self) -> str:
        return f"{self.label}: {self.value}{self.unit if self.unit else ''}"


def send_email_handler():

    msg_subject = "Fridge door is open!"
    msg_text = "Your left your fridge door open for a long time.\n"

    msg_from = os.getenv("EMAIL_FROM")
    msg_to = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_APP_SPECIFIC_PW")
    host = os.getenv("EMAIL_HOST")
    port = os.getenv("EMAIL_PORT")

    try:
        if None in [msg_from, msg_to, password, host, port]:
            raise ValueError("\nEnvironment variables for sending email notifications are not set.")
    except ValueError as e:
        print(e)
        print("Cannot send email.")
        return None

    port = int(port)

    send_email(host=host,
               port=port,
               starttls=True,
               msg_from=msg_from,
               msg_to=msg_to,
               password=password,
               msg_text=msg_text,
               msg_subject=msg_subject
               )
    print(" Sent email.")

    return None
