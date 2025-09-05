##!/usr/bin/python
import spidev
from time import sleep
from gpiozero import Buzzer
import sys

print("Start script...")

buzzer = Buzzer(13)
 
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
 
 
def readChannel(channel):
  val = spi.xfer2([1,(8+channel)<<4,0])
  data = ((val[1]&3) << 8) + val[2]
  return data
  
if __name__ == "__main__":
  while True:  
    v=(readChannel(0)/1023.0)*3.3
    dist = 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 301.439
    #clear line
   

    print(" "*30, "\r",  f"Dist: {str(round(dist, 1)).ljust(6)}cm", end=" ")

    if dist > 50:
      buzzer.off()
      print("Buzzer off", end="\r")
    else:
      buzzer.on()
      print("Buzzer on", end="\r")
    sleep(0.1)



