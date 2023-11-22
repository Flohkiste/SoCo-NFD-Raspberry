import pathlib
import threading as th
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
timer = None


def resetCurrentPlaylist():
    global currentPlaylist
    print("Times up")
    currentPlaylist = -1


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
    print("Join Groups")
    updateObjects()
    Küche[1].join(Küche[0])


def joinGroup():
    print("Join Group")
    updateObjects()
    x = False
    if Küche[0].get_current_transport_info()["current_transport_state"] == "PLAYING":
        Küche[0].pause()
        x = True

    Wohnzimmer.join(Küche[0])
    Küche[1].join(Küche[0])

    if x:
        while grouped == False:
            time.sleep(2)
            checkIfGrouped()

        Küche[0].play()


def resetGroups():
    print("Reset")
    x = False
    if Küche[0].get_current_transport_info()["current_transport_state"] == "PLAYING":
        Küche[0].pause()
        x = True

    Wohnzimmer.unjoin()
    Küche[1].unjoin()
    joinGroups()
    updateObjects()

    if x:
        while grouped == False:
            time.sleep(2)
            checkIfGrouped()

        Küche[0].play()


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


import time

last_read_time = time.time()
debounce_time = 0.1  # 100 milliseconds


def valueVolumeChanged(value, direction):
    global last_read_time
    current_time = time.time()
    if current_time - last_read_time > debounce_time:
        value = volumeEncoder.getValue()
        direction = volumeEncoder.direction
        print("Volume: {}, Direction: {}".format(value, direction))
        last_read_time = current_time


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
    print("Grouping Button Pressed")
    checkIfGrouped()
    print(grouped)

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
    global iplay, currentPlaylist, timer
    y = 0
    updateScan()
    for x in range(len(lastScans)):
        if lastScans[x] != None:
            y += 1

    if (y == 2) & (currentPlaylist != lastScans[0]) & (iplay == False):
        print("play")
        for x in range(len(lastScans)):
            if lastScans[x] != None:
                playlistFromId(int(lastScans[x]))
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
        timer = th.Timer(5.0, resetCurrentPlaylist)
        timer.start()
        print("Timer Started")
        iplay = False
    else:
        print(" ")


def playlistFromId(id):
    global currentPlaylist, timer
    if timer != None:
        timer.cancel()
        print("Timer canceled")
        timer = None

    if currentPlaylist == id:
        Küche[0].play()
    else:
        Küche[0].clear_queue()
        currentPlaylist = id
        ShareLinkPlugin.add_share_link_to_queue(myShare, Playlists[id])
        Küche[0].play_from_queue(0)


GPIO.setmode(GPIO.BCM)

volumeEncoder = Encoder(26, 17, valueVolumeChanged)
# playButtonPin = 27
groupingButtonPin = 16
shuffleButtonPin = 27
scanner = SimpleMFRC522()
lastScans = [None, None, None, None]

GPIO.setup(groupingButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(shuffleButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(
    groupingButtonPin, GPIO.FALLING, callback=groupingButtonPressed, bouncetime=5000
)
GPIO.add_event_detect(
    shuffleButtonPin, GPIO.FALLING, callback=shuffleButtonPressed, bouncetime=1000
)


resetGroups()
setupPlaylists()

try:
    while True:
        checkForScan()
except KeyboardInterrupt:
    GPIO.cleanup()
