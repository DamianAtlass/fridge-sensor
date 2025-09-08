##!/usr/bin/python
import sys
from typing import Callable, Any
from numpy import zeros
from spidev import SpiDev
from time import sleep, time
from gpiozero import Buzzer, LED
from signal import signal, SIGINT
from send_mail import send_email
import os
from dotenv import load_dotenv


def silencer(func: Callable[..., Any], b: bool) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> None:
        if not b:
            func(*args, **kwargs)
    return wrapper


def beeper(on: Callable[..., Any], off: Callable[..., Any]) -> Callable[..., Any]:
    def beeper_wrapper(beeps:int=1, t:int=0.2) -> None:
        for i in range(beeps):
            on()
            sleep(t)
            off()
            if i!=beeps-1:
                sleep(t)
    return beeper_wrapper

def evaluate_counter(coutner: int, time_windows:list[int]) -> int:
    time_windows.append(coutner)
    time_windows.sort()
    return time_windows.index(coutner)


def signal_handler(sig, frame):
    print('\nProgram terminated!')
    sys.exit(0)

def send_email_handler():

    msg_subject = "Fridge door is open!"
    msg_text = "Your left your fridge door open for a long time.\n"

    msg_from = os.getenv("EMAIL_FROM")
    msg_to = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_APP_SPECIFIC_PW")
    host = os.getenv("EMAIL_HOST")
    port = int(os.getenv("EMAIL_PORT"))

    try:
        if None in [msg_from, msg_to, password, host, port]:
            raise ValueError("Some environment variables are not set.")
    except ValueError as e:
        print(e)
        print("Cannot send email.")
        return None

    send_email(host=host,
               port=port,
               starttls=True,
               msg_from=msg_from,
               msg_to=msg_to,
               password=password,
               msg_text=msg_text,
               msg_subject=msg_subject
               )
    print("Sent email.")

    return None


def main():
    load_dotenv()

    # register signal handler
    signal(SIGINT, signal_handler)
    # read runtime parameters
    silence_buzzer = "-s" in sys.argv

    if "-o" in sys.argv:
        n = sys.argv.index("-o")+1
        offset = float(sys.argv[n])
    else:
        offset = 0.5

    if "-nomail" in sys.argv:
        send_notification = False
    else:
        send_notification = True

    #setup buzzer
    buzzer = Buzzer(13)
    buzzer_on = silencer(buzzer.on, silence_buzzer)
    buzzer_off = silencer(buzzer.off, silence_buzzer)
    beep = beeper(on=buzzer_on, off=buzzer_off)

    #setup led
    led = LED(16)
    blink = beeper(on=led.on, off=led.off)

    #setup sensor
    spi = SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000

    def readChannel(channel):
        # formula very inaccurate
        val = spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((val[1] & 3) << 8) + val[2]
        return data

    def take_measurment():
        v = (readChannel(0) / 1023.0) * 3.3
        return 16.2537 * v ** 4 - 129.893 * v ** 3 + 382.268 * v ** 2 - 512.611 * v + 301.439

    def get_distace(n: int = 100, t: int = 0.01) -> float:
        i = 0
        arr = zeros(n)
        while i < n:
            arr[i] = take_measurment()
            i += 1
            sleep(t)
        return arr.mean()

    print(f"Start script{' silently' if silence_buzzer else ''}...Press Ctrl+C to exit.")
    blink(t=0.1)

    # calibrate and compensate measuring for errors
    offset = 1 if offset is None else offset
    threshold = get_distace() + offset
    print("Threshold: ", round(threshold, 2), ", Offset:", offset)

    time_windows = [5, 10, 15, 20]
    noise_level = ["no noise", "slightly noisy", "slightly noisy", "very noisy", "very noisy - email was sent"]

    counter_door_possibly_open = 0
    time_blinker = time()
    while True:
        t_start = time()
        sleep(0.1)

        # clear line ending
        print(" " * 15, "\r", end="")

        dist = get_distace()
        print(f"\rDist: {str(round(dist, 1)).rjust(5)}cm", end="")

        if door_possibly_open:= threshold < dist:
            counter_door_possibly_open += 1
        else:
            counter_door_possibly_open = 0

        alarm_level = evaluate_counter(counter_door_possibly_open, time_windows.copy())

        print(", Door","!open!" if door_possibly_open else "closed", end="")
        t_end = time()
        print(", Iteration time: ", str(round(t_end - t_start, 2)).ljust(2),"s", end="")
        print(", Counter: ", str(counter_door_possibly_open).ljust(2), end="")
        print(f", Alarm level on {alarm_level}/{len(time_windows)} ({noise_level[alarm_level]})" , end="")


        if counter_door_possibly_open == time_windows[0]:
            beep(2)

        elif counter_door_possibly_open == time_windows[1]:
            beep(3)

        elif counter_door_possibly_open > time_windows[2]:
            beep()

        elif send_notification and counter_door_possibly_open > time_windows[3]:
            send_email_handler()

        # status blink
        if time() - time_blinker > 5:
            time_blinker = time()
            blink(t=0.1)
if __name__ == "__main__":
    main()



