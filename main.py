import os

from player import MusicPlayer
from filetypes import Song
import vlc
import time

doot = Song(path="/media/arnalljm/windows/Users/arnal/Music/Nintendo/Disc 1/1-01 Channel Menu.mp3")
noot = Song(path="/media/arnalljm/windows/Users/arnal/Music/Nintendo/Disc 1/1-02 Breath of the Wild.mp3")
# thing = vlc.MediaPlayer('vlc "'+doot.path+'" "'+ noot.path+'"')
# thing.retain()
# print(thing.get_media())
# thing.play()
# time.sleep(0.1)
# print(thing.get_media())
# print(thing.get_media())
# print(thing.get_length())
# print(thing.get_time())
# print(thing.get_position())
# print(thing.get_state())
# print(thing.audio_get_track_count())
# print(thing.audio_get_track())
# print(thing.audio_set_track(1))
# time.sleep(2)
# thing.set_position(0.99)
# time.sleep(2)
# print(thing.get_state())
# # time.sleep(2)
# # thing.stop()

instance = vlc.Instance()
media = instance.media_new(doot.path)
media_player = instance.media_list_player_new()
media_list = instance.media_list_new()
print(len(media_list))
media_list.insert_media(media, 0)
print(len(media_list))
media_player.set_media_list(media_list)
manager = media_player.get_media_player().event_manager()
# media_player.play()
print(media_player.get_state())
print(type(manager))
print([thing for thing in dir(manager)])

def doot(x):
    print("doot")
    # media_player.pause()

# manager.event_attach(vlc.EventType.MediaListPlayerPlayed,doot)
manager.event_attach(vlc.EventType.MediaPlayerOpening,doot)


media_player.play()
time.sleep(4)
intro = instance.media_new(noot.path)
media_list.insert_media(intro, 1)
print(len(media_list))
time.sleep(4)
media_player.next()
media_list.remove_index(0)
print(media_list.item_at_index(0))
print(media_list.item_at_index(1))
media_list.insert_media(media, 1)
print(media_list[0], media_list[1])
time.sleep(4)
print(media_player.next())
print(len(media_list))
time.sleep(4)
