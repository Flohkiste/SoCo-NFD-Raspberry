import time
import RPi.GPIO as GPIO
from encoder import Encoder


def valueChanged(value, direction):
    print("* New value: {}, Direction: {}".format(value, direction))


def button_pressed_callback(channel):
    print("Button pressed!")


GPIO.setmode(GPIO.BCM)

e1 = Encoder(26, 17, valueChanged)

button_pin = 16  # Changed to 16
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(
    button_pin, GPIO.FALLING, callback=button_pressed_callback, bouncetime=300
)

try:
    while True:
        time.sleep(5)
        print("Value is {}".format(e1.getValue()))
except KeyboardInterrupt:
    GPIO.cleanup()
