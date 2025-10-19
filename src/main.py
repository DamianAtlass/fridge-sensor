##!/usr/bin/python
import sys
from numpy import zeros
from spidev import SpiDev
from time import sleep, time
from gpiozero import Buzzer, LED
from signal import signal, SIGINT
import os
from dotenv import load_dotenv
import csv
from datetime import datetime
from utils import silencer, beeper, LogEntry, send_email_handler

BUZZER_PIN = 13
LED_PIN = 16

def evaluate_counter(counter_door_open: int, time_windows:list[int], counter_door_ajar: int) -> int:
    """ Return the alarm level and take into consideration if the door is ajar.
    """
    time_windows.append(counter_door_open)
    time_windows.sort()
    alarm_1 = time_windows.index(counter_door_open)
    alarm_2 = 3 if counter_door_ajar > 3 else 0
    return max(alarm_1, alarm_2)


def signal_handler(sig, frame):
    print('\nProgram terminated!')
    sys.exit(0)


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

    if "-j" in sys.argv:
        n = sys.argv.index("-j") + 1
        # offset_ajar is used to determine if the door is almost closed, but not completely, indicating unintuitive behaviour and more aggressive beeping
        offset_ajar = float(sys.argv[n])
    else:
        offset_ajar = 12

    if "-nomail" in sys.argv:
        send_notification = False
    else:
        send_notification = True

    #setup buzzer
    buzzer = Buzzer(BUZZER_PIN)
    buzzer_on = silencer(buzzer.on, silence_buzzer)
    buzzer_off = silencer(buzzer.off, silence_buzzer)
    beep = beeper(on=buzzer_on, off=buzzer_off)

    #signal running script
    beep(1)

    #setup led
    led = LED(LED_PIN)
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
    threshold_door_open = get_distace() + offset
    threshold_ajar = get_distace() + offset_ajar
    print(f"threshold_door_open: {round(threshold_door_open, 2)}, threshold_ajar: {round(threshold_ajar, 2)}, Buzzer silent: {silence_buzzer == True}, Send mails: {send_notification}")

    time_windows = [15, 30, 60, 120]
    noise_level = ["no noise", "slightly noisy", "slightly noisy", "very noisy", f"very noisy"]

    counter_door_open = 0
    counter_door_ajar = 0
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

        if door_open:= dist > threshold_door_open:
            counter_door_open += 1
        else:
            counter_door_open = 0
            counter_door_ajar = 0

        if door_ajar:= door_open and dist < threshold_ajar:
            counter_door_ajar += 1
        else:
            counter_door_ajar = 0
        alarm_level = evaluate_counter(counter_door_open, time_windows.copy(), counter_door_ajar)

        door_status = "ajar" if door_ajar else "open" if door_open else "closed"

        log_list.append(LogEntry("Door", door_status))
        t_end = time()

        if counter_door_open == time_windows[0]:
            beep(2)

        elif counter_door_open == time_windows[1]:
            beep(3)

        if counter_door_open > time_windows[2] or counter_door_ajar > 3:
            beep()

        if send_notification and counter_door_open == time_windows[3]:
            send_email_handler()


        ### logging etc
        #log on console
        log_list.append(LogEntry("Dist", str(round(dist, 2)).rjust(5), "cm"))
        log_list.append(LogEntry("Iteration time", str(round(t_end - t_start, 2)).ljust(2), "s"))
        log_list.append(LogEntry("Counter_open", str(counter_door_open).ljust(2)))
        log_list.append(LogEntry("Counter_ajar", str(counter_door_ajar).ljust(2)))
        loudness_lable = 'noisy' if counter_door_ajar > 3 else noise_level[alarm_level]
        log_list.append(LogEntry("Alarm level", f"{alarm_level}/{len(time_windows)}", " " + loudness_lable))

        log_string = ", ".join([str(l) for l in log_list])
        print(log_string, end="")

        # clear line ending
        print(" " * 15, "\r", end="")

        # log in file
        log_list.insert(0, LogEntry("t", datetime.now()))
        if door_ajar or door_open:
            write_to_logfile(logs=log_list, log_file ="logs.csv")

        # status blink
        if time() - time_blinker > 5:
            time_blinker = time()
            blink(t=0.1)
if __name__ == "__main__":
    main()



