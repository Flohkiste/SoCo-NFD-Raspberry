import pathlib
from threading import Timer
from encoder import Encoder
import RPi.GPIO as GPIO
from soco import SoCo
from soco.plugins.sharelink import *
import time
from mfrc522 import SimpleMFRC522


Wohnzimmer = SoCo("192.168.150.28")
Küche = [SoCo("192.168.150.30"), SoCo("192.168.150.39")]
Playlists = []
myShare = ShareLinkPlugin(Küche[0])
currentPlaylist = -1
grouped = False
iplay = False


def setupPlaylists():
    print("Opening file...")
    filepath = str(pathlib.Path(__file__).parent.resolve()) + "/playlists.txt"
    playlistFile = open(filepath, "r")
    print("Reading lines...")
    line_list = playlistFile.readlines()
    print(f"Read {len(line_list)} lines.")

    for line in line_list:
        Playlists.append(line.strip())

    playlistFile.close()


def updateObjects():
    global Wohnzimmer, Küche
    Wohnzimmer = SoCo("192.168.150.28")
    Küche = [SoCo("192.168.150.30"), SoCo("192.168.150.39")]


def joinGroups():
    Küche[1].join(Küche[0])


def joinGroup():
    x = False
    if Küche[0].get_current_transport_info()["current_transport_state"] == "PLAYING":
        Küche[0].pause()
        x = True

    resetGroups()
    Wohnzimmer.join(Küche[0])
    Küche[1].join(Küche[0])

    if x:
        t = Timer(5.0, Küche[0].play())
        t.start


def resetGroups():
    Wohnzimmer.unjoin()
    Küche[0].unjoin()
    Küche[1].unjoin()
    joinGroups()


def checkIfGrouped():
    global grouped
    updateObjects()
    group = next(g for g in Küche[0].all_groups if g.coordinator is Küche[0])
    num_devices = len(group.members)
    if num_devices <= 3:
        grouped = False
    else:
        grouped = True


def clearQueue():
    global grouped
    for x in Küche:
        Küche[x].clear_queue()

    if grouped:
        Wohnzimmer.clear_queue()


def valueVolumeChanged(value, direction):
    print("Volume: {}, Direction: {}".format(value, direction))


def playButtonPressed(channel):
    updateObjects()
    if Küche[0].get_current_transport_info()["current_transport_state"] == "PLAYING":
        Küche[0].stop()
    elif (
        Küche[0].get_current_transport_info()["current_transport_state"]
        == "PAUSED_PLAYBACK"
    ):
        Küche[0].play()


def groupingButtonPressed(channel):
    global grouped
    checkIfGrouped()
    if grouped:
        resetGroups()
        grouped = False
    else:
        joinGroup()
        grouped = True


def shuffleButtonPressed(channel):
    if Küche[0].shuffle:
        Küche[0].play_mode = "NORMAL"
    else:
        Küche[0].play_mode = "SHUFFLE"


def updateScan():
    global lastScans
    lastScans[3] = lastScans[2]
    time.sleep(0.001)
    lastScans[2] = lastScans[1]
    time.sleep(0.001)
    lastScans[1] = lastScans[0]
    time.sleep(0.001)
    lastScans[0] = scanner.read_no_block()[1]


def checkForScan():
    global iplay, currentPlaylist
    y = 0
    updateScan()
    for x in range(len(lastScans)):
        if lastScans[x] != None:
            y += 1

    if (y == 2) & (currentPlaylist != lastScans[0]) & (iplay == False):
        print("play")
        for x in range(len(lastScans)):
            if lastScans[x] != None:
                currentPlaylist = int(lastScans[x])
                print(currentPlaylist)
                playlistFromId(int(currentPlaylist))
                break
        print(currentPlaylist)
        iplay = True
    elif (
        (y < 2)
        & (iplay == True)
        & (
            Küche[0].get_current_transport_info()["current_transport_state"]
            == "PLAYING"
        )
    ):
        print("Stop")
        Küche[0].pause()
        iplay = False
    else:
        print(" ")


def playlistFromId(id):
    global currentPlaylist
    Küche[0].clear_queue()
    currentPlaylist = id
    ShareLinkPlugin.add_share_link_to_queue(myShare, Playlists[id])
    Küche[0].play_from_queue(0)


GPIO.setmode(GPIO.BCM)

volumeEncoder = Encoder(26, 17, valueVolumeChanged)
# playButtonPin = 27
groupingButtonPin = 16
# shuffleButtonPin = 0
scanner = SimpleMFRC522()
lastScans = [None, None, None, None]

GPIO.setup(groupingButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(
    groupingButtonPin, GPIO.FALLING, callback=groupingButtonPressed, bouncetime=300
)
# GPIO.add_event_detect(
#    playButtonPin, GPIO.FALLING, callback=playButtonPressed, bouncetime=300
# )


resetGroups()
setupPlaylists()

try:
    while True:
        checkForScan()
except KeyboardInterrupt:
    GPIO.cleanup()
