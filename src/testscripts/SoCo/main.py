import time
from soco import SoCo
from soco.plugins.sharelink import *


room2ip = "192.168.150.29"

room = SoCo("192.168.150.38")
room.clear_queue()
print(room.player_name)
room.unjoin()


# myShare = ShareLinkPlugin(room)
# ShareLinkPlugin.add_share_link_to_queue(myShare, playlist)

room2 = SoCo(room2ip)
print(room2.player_name)
room2.unjoin()


# ...

room2.join(room)


# Wait for a moment to allow the group information to update
time.sleep(2)

# Re-instantiate the SoCo objects
room = SoCo("192.168.150.38")
room2 = SoCo(room2ip)


# Now check the group members
group = next(g for g in room.all_groups if g.coordinator is room)
print(group)
# Get the number of devices in the group
num_devices = len(group.members)

print(f"There are {num_devices} devices in the group.")


myShare = ShareLinkPlugin(room)
ShareLinkPlugin.add_share_link_to_queue(
    myShare,
    "https://open.spotify.com/playlist/4aRqsGxLhQcdsypFQ8O0f3?si=9c45a7d657f84153",
)

room.play()
