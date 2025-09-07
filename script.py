##!/usr/bin/python
import sys
from typing import Callable, Any
import numpy as np
import spidev
from time import sleep, time
from gpiozero import Buzzer, LED
import signal

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
    print('\nProgramm terminated!')
    sys.exit(0)


def main():
    # register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    # read runtime parameters
    silence_buzzer = "-s" in sys.argv

    if "-o" in sys.argv:
        n = sys.argv.index("-o")+1
        offset = float(sys.argv[n])
    else:
        offset = 0.5

    #setup buzzer
    buzzer = Buzzer(13)
    buzzer_on = silencer(buzzer.on, silence_buzzer)
    buzzer_off = silencer(buzzer.off, silence_buzzer)
    beep = beeper(on=buzzer_on, off=buzzer_off)

    #setup led
    led = LED(16)
    blink = beeper(on=led.on, off=led.off)

    #setup sensor
    spi = spidev.SpiDev()
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
        arr = np.zeros(n)
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

    time_windows = [5, 10, 15]
    noise = ["no noise", "slightly noisy", "slightly noisy", "very noisy"]

    counter_door_possibly_open = 0
    time_blinker = time()
    while True:
        t_start = time()
        sleep(0.1)

        # clear line
        print(" " * 60, "\r", end="")

        dist = get_distace()
        print(f"\rDist: {str(round(dist, 1)).rjust(5)}cm", end="")

        if door_possibly_open:= threshold < dist:
            counter_door_possibly_open += 1
        else:
            counter_door_possibly_open = 0

        alarmlevel = evaluate_counter(counter_door_possibly_open, time_windows.copy())

        print(", Door","!open!" if door_possibly_open else "closed", end="")
        t_end = time()
        print(", iteration time: ", str(round(t_end - t_start, 2)).ljust(2),"s", end="")
        print(", counter: ", str(counter_door_possibly_open).ljust(2), end="")
        print(f", Alarmlevel on {alarmlevel}/{len(time_windows)} ({noise[alarmlevel]})" , end="")


        if counter_door_possibly_open == time_windows[0]:
            beep(2)

        elif counter_door_possibly_open == time_windows[1]:
            beep(3)

        elif counter_door_possibly_open > time_windows[2]:
            beep()

        # status blink
        if time() - time_blinker > 5:
            time_blinker = time()
            blink(t=0.1)
if __name__ == "__main__":
    main()



