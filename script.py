##!/usr/bin/python
from builtins import function

import spidev
from time import sleep
from gpiozero import Buzzer
import sys
from typing import Callable, Any

def readChannel(channel):
  val = spi.xfer2([1,(8+channel)<<4,0])
  data = ((val[1]&3) << 8) + val[2]
  return data


def main():
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
            if b:
                func(*args, **kwargs)
        return wrapper

    buzzer_on = silencer(buzzer.on, SILENCE_BUZZER)
    buzzer_off= silencer(buzzer.off, SILENCE_BUZZER)


    while True:
        v = (readChannel(0) / 1023.0) * 3.3
        dist = 16.2537 * v ** 4 - 129.893 * v ** 3 + 382.268 * v ** 2 - 512.611 * v + 301.439
        # clear line

        print(" " * 30, "\r", f"Dist: {str(round(dist, 1)).ljust(6)}cm", end=" ")

        if dist > 50:
            buzzer_off()
            print("Buzzer off", "(mute)" if SILENCE_BUZZER else "", end="\r")
        else:
            buzzer_on()
            print("Buzzer on","(mute)" if SILENCE_BUZZER else "", end="\r")
        sleep(0.1)


if __name__ == "__main__":
    main()



