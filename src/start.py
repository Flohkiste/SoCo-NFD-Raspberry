from encoder import Encoder
import RPi.GPIO as GPIO
from soco import SoCo
from soco.plugins.sharelink import *
import time

Wohnzimmer = SoCo("192.168.150.28")
Küche = [SoCo("192.168.150.30"), SoCo("192.168.150.39")]

grouped = False


def joinGroups():
    Küche[1].join(Küche[0])


def joinGroup():
    resetGroups()
    Wohnzimmer.join(Küche[0])
    Küche[1].join(Küche[0])


def resetGroups():
    Wohnzimmer.unjoin()
    Küche[0].unjoin()
    Küche[1].unjoin()
    joinGroups()


def clearQueue():
    for x in Küche:
        Küche[x].clear_queue()

    if grouped:
        Wohnzimmer.clear_queue()


def valueVolumeChanged(value, direction):
    print("Volume: {}, Direction: {}".format(value, direction))


def playButtonPressed(value, direction):
    print("Play: {}, Direction: {}".format(value, direction))


def groupingButtonPressed():
    if grouped:
        resetGroups
        grouped = False
    else:
        joinGroup
        grouped = True


def shuffleButtonPressed():
    print("Shuffle button pressed")


GPIO.setmode(GPIO.BCM)

volumeEncoder = Encoder(26, 17, valueVolumeChanged)
# playButtonPin = 0
shuffleButtonPin = 16
# groupingButtonPin = 0

GPIO.setup(shuffleButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(
    shuffleButtonPin, GPIO.FALLING, callback=shuffleButtonPressed, bouncetime=300
)
# GPIO.add_event_detect(
#    playButtonPin, GPIO.FALLING, callback=playButtonPressed, bouncetime=300
# )


joinGroups()

try:
    while True:
        time.sleep(5)
        print("Running")
except KeyboardInterrupt:
    GPIO.cleanup()
