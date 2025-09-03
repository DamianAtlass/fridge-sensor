from time import sleep
from gpiozero import Buzzer
print("Start script...")

buzzer = Buzzer(13)
print(buzzer)
buzzer.on()
sleep(0.3)
buzzer.off()
