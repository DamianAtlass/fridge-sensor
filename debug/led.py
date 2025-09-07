from gpiozero import Buzzer, LED
from time import sleep

led = LED(16)
led.on()
sleep(1)
led.off()
