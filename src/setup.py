import pathlib
from mfrc522 import SimpleMFRC522

playlists = []
iDs = []
scanner = SimpleMFRC522()


def setPlaylists():
    global playlists, scanner, iDs
    filepathPlaylists = str(pathlib.Path(__file__).parent.resolve()) + "/playlists.txt"
    filepathIDs = str(pathlib.Path(__file__).parent.resolve()) + "/nfcIDs.txt"
    playlistFile = open(filepathPlaylists, "w")
    idFile = open(filepathIDs, "w")

    while True:
        print(
            "Please enter the link to the associated playlist, write S to save the playlists:"
        )
        playlist = input("")
        if playlist == "S":
            break
        else:
            print("Please place the RFID chip on the scanner")
            id = scanner.read()[0]
            playlists.append(playlist + "\n")
            iDs.append(id + "\n")
            # scanner.write(str(len(playlists) - 1))

    playlistFile.writelines(playlists)
    idFile.writelines(iDs)
    playlistFile.close()
    idFile.close()


setPlaylists()
