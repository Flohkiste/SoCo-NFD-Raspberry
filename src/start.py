from encoder import Encoder
import RPi.GPIO as GPIO
from soco import SoCo
from soco.plugins.sharelink import *
import time

WohnzimmerSub = SoCo("192.168.150.34")
WohnzimmerArc = SoCo("192.168.150.28")
WohnzimmerR = SoCo("192.168.150.35")
WohnzimmerL = SoCo("192.168.150.29")
KücheR = SoCo("192.168.150.30")
KücheL = SoCo("192.168.150.36")
Klavier = SoCo("192.168.150.39")

Wohnzimmer = [
    SoCo("192.168.150.34"),
    SoCo("192.168.150.28"),
    SoCo("192.168.150.35"),
    SoCo("192.168.150.29"),
]
Küche = [SoCo("192.168.150.30"), SoCo("192.168.150.36"), SoCo("192.168.150.39")]


def joinGroups():
    for x in Wohnzimmer:
        x += 1
        if x == 4:
            break

        Wohnzimmer[x].join(Wohnzimmer[0])

    for x in Küche:
        x += 1
        if x == 3:
            break

        Küche[x].join(Küche[0])


def resetGroups():
    for x in Wohnzimmer:
        x += 1
        if x == 4:
            break

        Wohnzimmer[x].unjoin()

    for x in Küche:
        x += 1
        if x == 3:
            break

        Küche[x].unjoin()

    joinGroups()


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
