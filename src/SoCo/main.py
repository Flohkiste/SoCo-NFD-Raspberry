from soco import SoCo
from soco.plugins.sharelink import *

raum = input("Raum: ")
room = SoCo(raum)
room.clear_queue()
print(room.player_name)

playlist = input("Playlist: ")
myShare = ShareLinkPlugin(room)
ShareLinkPlugin.add_share_link_to_queue(myShare, playlist)

room.play()
