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
import csv
from datetime import datetime


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

class LogEntry:
    def __init__(self, label : str, value : Any, unit : str = None) -> None :
        self.label = label
        self.value = value
        self.unit = unit

    def __str__(self) -> str:
        return f"{self.label}: {self.value}{self.unit if self.unit else ''}"

def write_to_logfile(logs : list[LogEntry], log_file : str = "logfile.csv") -> None:
    mode = 'w' if not os.path.isfile(log_file) else 'a'

    with open(log_file, mode, newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        if mode == 'w':
            writer.writerow([l.label for l in logs])
        writer.writerows([[l.value for l in logs]]) # needs double list


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

    if "-b" in sys.argv:
        n = sys.argv.index("-b") + 1
        # threshold_2 is used to determine if the door is almost closed, but not completely, indicating
        # unintuitive behaviour and more aggressive beeping
        threshold_2 = float(sys.argv[n])
    else:
        threshold_2 = 12

    if "-nomail" in sys.argv:
        send_notification = False
    else:
        send_notification = True

    #setup buzzer
    buzzer = Buzzer(13)
    buzzer_on = silencer(buzzer.on, silence_buzzer)
    buzzer_off = silencer(buzzer.off, silence_buzzer)
    beep = beeper(on=buzzer_on, off=buzzer_off)

    #signal running script
    beep(1)

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

    print(f"Start script...Press Ctrl+C to exit.")
    blink(t=0.1)

    # calibrate and compensate measuring for errors
    offset = 1 if offset is None else offset
    threshold = get_distace() + offset
    print(f"Threshold: {round(threshold, 2)}, Offset: {offset}, Threshold2: {round(threshold_2, 2)}, Buzzer silent: {silence_buzzer == True}, Send mails: {send_notification}")

    time_windows = [15, 30, 60, 120]
    noise_level = ["no noise", "slightly noisy", "slightly noisy", "very noisy", f"very noisy"]

    counter_door_possibly_open = 0
    counter_door_a_little_open = 0
    time_blinker = time()

    rotating_symbols = list("◴◷◶◵")
    i = 0
    while True:
        log_list = []
        t_start = time()
        sleep(0.1) # keep log visible for a short while



        # rotate some symbols to indicate the program running on the console
        print(rotating_symbols[i % len(rotating_symbols)], end=" ")
        if i == len(rotating_symbols)-1:
            i = 0
        else:
            i += 1

        dist = get_distace()

        if door_open:= dist > threshold:
            counter_door_possibly_open += 1
        else:
            counter_door_possibly_open = 0
            counter_door_a_little_open = 0

        if door_a_little_open:= door_open:
            if dist < threshold + threshold_2:
                counter_door_a_little_open += 1
            else:
                counter_door_a_little_open = 0
        alarm_level = evaluate_counter(counter_door_possibly_open, time_windows.copy())

        door_status = "open" if door_open else "a bit open" if door_a_little_open else "closed"

        log_list.append(LogEntry("Door", door_status))
        t_end = time()

        #log on console
        log_list.append(LogEntry("Dist", str(round(dist, 2)).rjust(5), "cm"))
        log_list.append(LogEntry("Iteration time", str(round(t_end - t_start, 2)).ljust(2),"s"))
        log_list.append(LogEntry("Counter", str(counter_door_possibly_open).ljust(2)))
        log_list.append(LogEntry("Counter_2", str(counter_door_a_little_open).ljust(2)))
        loudness_lable = 'noisy' if counter_door_a_little_open > 3 else noise_level[alarm_level]
        log_list.append(LogEntry("Alarm level", f"{alarm_level}/{len(time_windows)}", " " + loudness_lable))

        log_string = ", ".join([str(l) for l in log_list])
        print(log_string, end="")
        # clear line ending
        print(" " * 15, "\r", end="")

        #log in file
        log_list.insert(0, LogEntry("t", datetime.now()))
        write_to_logfile(logs=log_list, log_file = "logs.csv")

        if counter_door_possibly_open == time_windows[0]:
            beep(2)

        elif counter_door_possibly_open == time_windows[1]:
            beep(3)

        if counter_door_possibly_open > time_windows[2] or counter_door_a_little_open > 3:
            beep()

        if send_notification and counter_door_possibly_open == time_windows[3]:
            send_email_handler()

        # status blink
        if time() - time_blinker > 5:
            time_blinker = time()
            blink(t=0.1)
if __name__ == "__main__":
    main()



