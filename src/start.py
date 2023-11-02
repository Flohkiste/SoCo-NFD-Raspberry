from encoder import Encoder
import RPi.GPIO as GPIO
from soco import SoCo
from soco.plugins.sharelink import *
import time

WohnzimmerSub = "192.168.150.34"
WohnzimmerArc = "192.168.150.28"
WohnzimmerR = "192.168.150.35"
WohnzimmerL = "192.168.150.29"
KücheR = "192.168.150.30"
KücheL = "192.168.150.36"
Klavier = "192.168.150.39"


def valueVolumeChanged(value, direction):
    print("Volume: {}, Direction: {}".format(value, direction))


def valuePlayChanged(value, direction):
    print("Play: {}, Direction: {}".format(value, direction))


def groupingButtonPressed():
    print("Grouping button pressed")


def shuffleButtonPressed():
    print("Shuffle button pressed")


GPIO.setmode(GPIO.BCM)

volumeEncoder = Encoder(26, 17, valueVolumeChanged)
# playEncoder = 0
shuffleButtonPin = 16
# groupingButtonPin = 0

GPIO.setup(shuffleButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(
    shuffleButtonPin, GPIO.FALLING, callback=shuffleButtonPressed, bouncetime=300
)

try:
    while True:
        time.sleep(5)
        print("Running")
except KeyboardInterrupt:
    GPIO.cleanup()
