import pathlib
import threading as th
from encoder import Encoder
import RPi.GPIO as GPIO
from soco import SoCo
from soco.plugins.sharelink import *
import time
from mfrc522 import SimpleMFRC522
from MyTimer import MyTimer


Wohnzimmer = SoCo("172.20.10.7")
Küche = SoCo("172.20.10.6")
Playlists = []
iDs = []
myShare = ShareLinkPlugin(Küche)
currentPlaylist = -1
grouped = False
iplay = False
timer = None
x = 0


def resetCurrentPlaylist():
    global currentPlaylist
    print("Times up")
    currentPlaylist = -1


def setupPlaylists():
    global Playlists, scanner, iDs
    filepathPlaylists = str(pathlib.Path(__file__).parent.resolve()) + "/playlists.txt"
    filepathIDs = str(pathlib.Path(__file__).parent.resolve()) + "/nfcIDs.txt"
    playlistFile = open(filepathPlaylists, "r")
    idFile = open(filepathIDs, "r")

    print("Reading lines...")
    line_list = playlistFile.readlines()
    print(f"Read {len(line_list)} lines.")

    for line in line_list:
        Playlists.append(line.strip())

    playlistFile.close()

    line_list = idFile.readlines()
    print(f"Read {len(line_list)} lines.")

    for line in line_list:
        iDs.append(int(line.strip()))  # Convert ID to integer

    idFile.close()


def updateObjects():
    global Wohnzimmer, Küche, volumeEncoder
    Wohnzimmer = SoCo("172.20.10.7")
    Küche = SoCo("172.20.10.6")


def joinGroups():
    print("Join Groups")
    updateObjects()


def joinGroup():
    print("Join Group")
    updateObjects()
    x = False
    if Küche.get_current_transport_info()["current_transport_state"] == "PLAYING":
        Küche.pause()
        x = True

    Wohnzimmer.join(Küche)

    if x:
        while grouped == False:
            time.sleep(2)
            checkIfGrouped()

        Küche.play()


def resetGroups():
    print("Reset")
    x = False
    if Küche.get_current_transport_info()["current_transport_state"] == "PLAYING":
        Küche.pause()
        x = True

    Wohnzimmer.unjoin()
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
    group = next(g for g in Küche.all_groups if g.coordinator is Küche)
    num_devices = len(group.members)
    if num_devices <= 3:
        grouped = False
    else:
        grouped = True


def clearQueue():
    global grouped
    Küche.clear_queue()

    if grouped:
        Wohnzimmer.clear_queue()


import threading

volume_change = 0
volume_lock = threading.Lock()


def applyVolumeChange():
    global volume_change
    with volume_lock:
        change = volume_change
        volume_change = 0
    Küche.group.set_relative_volume(change)


def valueVolumeChanged(value, direction):
    global volume_change

    print(value, direction)

    with volume_lock:
        if direction:
            print("R")
            volume_change += 1
        else:
            print("L")
            volume_change -= 1

    # Apply volume changes in a separate thread
    threading.Thread(target=applyVolumeChange).start()


def playButtonPressed(channel):
    updateObjects()
    if Küche.get_current_transport_info()["current_transport_state"] == "PLAYING":
        Küche.pause()
    elif (
        Küche.get_current_transport_info()["current_transport_state"]
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
    if Küche.shuffle:
        Küche.play_mode = "NORMAL"
    else:
        Küche.play_mode = "SHUFFLE"


def updateScan():
    global lastScans
    lastScans[3] = lastScans[2]
    time.sleep(0.001)
    lastScans[2] = lastScans[1]
    time.sleep(0.001)
    lastScans[1] = lastScans[0]
    time.sleep(0.001)
    try:
        lastScans[0] = scanner.read_no_block()[0]
    except Exception as e:
        if "AUTH ERROR" in str(e):
            pass  # Ignore the error
        else:
            raise  # Re-raise the error if it's not an "AUTH ERROR"


def checkForScan():
    global iplay, currentPlaylist, timer
    y = 0

    try:
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
                Küche.get_current_transport_info()["current_transport_state"]
                == "PLAYING"
            )
        ):
            print("Stop")
            Küche.pause()
            timer = MyTimer(30.0, resetCurrentPlaylist)
            timer.start()
            print("Timer Started")
            iplay = False
        else:
            print(" ")

    except Exception as e:
        if "AUTH ERROR" in str(e):
            pass  # Ignore the error
        else:
            raise  # Re-raise the error if it's not an "AUTH ERROR"


def playlistFromId(id):
    global currentPlaylist, timer, Küche
    Küche.play_mode = "SHUFFLE"
    if timer != None:
        print(f"Time left: {timer.elapsed_time()}")
        if timer.elapsed_time() <= 10:
            print("Skip")
            Küche.next()

        timer.cancel()
        print("Timer canceled")
        timer = None

    if currentPlaylist == iDs.index(id):
        Küche.play()
    else:
        Küche.clear_queue()
        currentPlaylist = iDs.index(id)
        ShareLinkPlugin.add_share_link_to_queue(myShare, Playlists[iDs.index(id)])
        Küche.play_from_queue(0)


GPIO.setmode(GPIO.BCM)

volumeEncoder = Encoder(26, 17, callback=valueVolumeChanged)
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
    shuffleButtonPin, GPIO.FALLING, callback=playButtonPressed, bouncetime=1000
)


resetGroups()
setupPlaylists()
Küche.volume = 10
print("Volume: {}".format(Küche.volume))
Küche.play_mode = "SHUFFLE"

try:
    while True:
        checkForScan()
except KeyboardInterrupt:
    GPIO.cleanup()
