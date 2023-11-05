Playlists = []


def setupPlaylists():
    print("Opening file...")
    playlistFile = open(
        "/Users/Flo/Documents/GitHub/SoCo-NFD-Raspberry/src/playlists.txt", "r"
    )
    print("Reading lines...")
    line_list = playlistFile.readlines()
    print(f"Read {len(line_list)} lines.")

    for line in line_list:
        Playlists.append(line.strip())

    playlistFile.close()


setupPlaylists()
