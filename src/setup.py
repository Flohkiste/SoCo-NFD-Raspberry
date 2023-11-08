import pathlib
from mfrc522 import SimpleMFRC522

Playlists = []
scanner = SimpleMFRC522()


def setPlaylists():
    global Playlists
    filepath = str(pathlib.Path(__file__).parent.resolve()) + "\playlists.txt"
    playlistFile = open(filepath, "w")

    while True:
        print(
            "Please enter the link to the associated playlist, write Finished to save the playlists:"
        )
        playlist = input("")
        print("Please place the RFID chip on the scanner")
        scanner.read()
        if playlist == "Finished":
            break
        else:
            Playlists.append(playlist + "\n")
            x = len(Playlists) - 1
            scanner.write(x)

    playlistFile.writelines(Playlists)
    playlistFile.close()


setPlaylists()
