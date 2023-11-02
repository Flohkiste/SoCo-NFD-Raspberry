from soco import SoCo
from soco.plugins.sharelink import *


my_zone = SoCo("192.168.150.38")
my_zone.clear_queue()
print(my_zone.player_name)
track = my_zone.get_current_track_info()
print(track["title"])
my_zone.play_mode = "NORMAL"

myShare = ShareLinkPlugin(my_zone)
ShareLinkPlugin.add_share_link_to_queue(
    myShare,
    "https://open.spotify.com/playlist/4aRqsGxLhQcdsypFQ8O0f3?si=9c45a7d657f84153",
)

print(my_zone.get_current_transport_info()["current_transport_state"])

track = my_zone.get_current_track_info()
print(track["title"])

print(my_zone.play_mode)
my_zone.play_mode = "SHUFFLE"
print(my_zone.play_mode)
my_zone.play()
