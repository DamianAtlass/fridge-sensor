##!/usr/bin/python
import sys
from typing import Callable, Any
import numpy as np
import spidev
from time import sleep, time
from gpiozero import Buzzer


def main():

    def readChannel(channel):
        #formula very inaccurate
        val = spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((val[1] & 3) << 8) + val[2]
        return data

    # read runtime parameters
    SILENCE_BUZZER = "-s" in sys.argv

    if "-o" in sys.argv:
        n = sys.argv.index("-o")+1
        OFFSET = float(sys.argv[n])
    else:
        OFFSET = 1


    #setup buzzer
    buzzer = Buzzer(13)

    #setup sensor
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000


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


    def beep(beeps:int=1, t:int=0.2):
        for i in range(beeps):
            buzzer_on()
            sleep(t)
            buzzer_off()
            if i!=beeps-1:
                sleep(t)

    def evaluate_counter(coutner: int, time_windows:list[int]) -> int:
        time_windows.append(coutner)
        time_windows.sort()
        return time_windows.index(coutner)


    print(f"Start script{' silently' if SILENCE_BUZZER else ''}...")


    buzzer_on = silencer(buzzer.on, SILENCE_BUZZER)
    buzzer_off= silencer(buzzer.off, SILENCE_BUZZER)

    # calibrate and compensate measuring for errors
    OFFSET = 1 if OFFSET is None else OFFSET
    threshold = get_distace() + OFFSET
    print("Threshold: ", round(threshold, 2), ", Offset:", OFFSET)

    time_windows = [5, 10, 15]
    noise = ["no noise", "slightly noisy", "slightly noisy", "very noisy"]

    counter_door_possibly_open = 0

    while True:
        t_start = time()
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

        sleep(0.1)

if __name__ == "__main__":
    main()



