import pathlib
from mfrc522 import SimpleMFRC522

Playlists = []
scanner = SimpleMFRC522()


def setPlaylists():
    global Playlists, scanner
    filepath = str(pathlib.Path(__file__).parent.resolve()) + "\playlists.txt"
    playlistFile = open(filepath, "w")

    while True:
        print(
            "Please enter the link to the associated playlist, write Finished to save the playlists:"
        )
        playlist = input("")
        if playlist == "Finished":
            break
        else:
            print("Please place the RFID chip on the scanner")
            scanner.read()
            Playlists.append(playlist + "\n")
            scanner.write(str(len(Playlists) - 1))

    playlistFile.writelines(Playlists)
    playlistFile.close()


setPlaylists()
