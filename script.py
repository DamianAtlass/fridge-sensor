##!/usr/bin/python
import threading

import spidev
from time import sleep
from gpiozero import Buzzer
import sys
from typing import Callable, Any
import numpy as np



def main():

    def readChannel(channel):
        val = spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((val[1] & 3) << 8) + val[2]
        return data

    print("Start script...")

    #setup buzzer
    buzzer = Buzzer(13)

    #setup sensor
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000

    SILENCE_BUZZER = "-s" in sys.argv

    def silencer(func: Callable[..., Any], b: bool) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> None:
            if not b:
                func(*args, **kwargs)
        return wrapper


    def take_measurment():
        v = (readChannel(0) / 1023.0) * 3.3
        return 16.2537 * v ** 4 - 129.893 * v ** 3 + 382.268 * v ** 2 - 512.611 * v + 301.439

    def get_distace(n: int = 100, t:int = 0.01) -> float:
        i = 0
        arr = np.zeros(n)
        while i < n:
            arr[i] = take_measurment()
            i += 1
            sleep(t)
        return arr.mean()


    buzzer_on = silencer(buzzer.on, SILENCE_BUZZER)
    buzzer_off= silencer(buzzer.off, SILENCE_BUZZER)

    # calibrate and compensate measuring for errors
    threshold = get_distace() + 1
    print("Threshold: ", threshold)


    while True:

        # clear line
        print(" " * 60, "\r", end="")

        dist = get_distace()
        print(f"Dist: {str(round(dist, 1)).ljust(6)}cm,", end=" ")

        if door_open:= threshold < dist:
            buzzer_on()
        else:
            buzzer_off()

        print("Door","  open" if door_open else "closed", end=" ")
        print("Buzzer","on" if buzzer.is_active else "off", "(mute)" if SILENCE_BUZZER else "", end="\r")
        sleep(0.1)

if __name__ == "__main__":
    main()



