import tkinter as tk
from tkinter import ttk
# from pygame.mixer import music
from song import SongStorage
import vlc
import numpy as np
import warnings


class MusicPlayer:
    def __init__(self):
        # self.startwindow()
        self.storage = None

        self.current_song = None
        self.current_media = None
        self.next_song = None
        self.next_media = None
        self.history = []

        self.instance = vlc.Instance()
        # self.media_list = self.instance.media_list_new()
        self.player = self.instance.media_player_new()
        # self.player.set_media_list(self.media_list)
        self.event_manager = self.player.event_manager()
        pass

    max_history_size = 10

    def generate_storage(self, directory_name=None):
        self.storage = SongStorage()
        if directory_name is not None:
            self.storage.import_library(directory_name)

    def load_storage(self, location=SongStorage.DEFAULT_SAVE):
        self.storage = SongStorage.load(location)

    def change_target(self, target, strength):
        # Requires np.array of ints!
        self.storage.change_target(target, strength)
        self._select_next()
        # self.set_next_media(self.next_song)

    def _select_next(self):
        try:
            draw = self.storage.select_song(self.max_history_size+1)
        except ValueError:
            print("No songs playable - current song will loop")
            return None
        for song in draw:
            if song not in self.history:
                # print(song.file_name)
                self.next_song = song
                self.next_media = self._create_media(song)
                return song
        print("All playable songs have already been played in history - ignoring history")
        self.next_song = draw[0]
        self.next_media = self._create_media(draw[0])
        return draw[0]
        # raise RuntimeError(f"At least {self.max_history_size+1} songs with nonzero probability required")

    def change_attributes(self, attributes, song=None):
        if song is None:
            song = self.current_song
        self.storage.set_attribute(song, attributes)

    def _create_media(self, song):
        return self.instance.media_new(song.path)

    def _first_start(self):
        # to be called the first time the music is played
        self._select_next()
        self.current_song = self.next_song
        self.current_media = self.next_media
        self.player.set_media(self.current_media)
        self._add_to_history(self.current_song)
        self.player.play()
        self._select_next()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.when_track_changed)
        self.print_current_info()

    def when_track_changed(self, _):
        # print("doot")
        # print(self.current_song.file_name, self.next_song.file_name)
        self.current_song = self.next_song
        self.current_media = self.next_media
        self._add_to_history(self.current_song)
        self._select_next()
        # self.player.release()
        self.player = self.instance.media_player_new()
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.when_track_changed)
        # self.player.set_position(0.)
        # print("joot")
        # print(self.player.will_play())
        self.player.set_media(self.current_media)
        # print("noot")
        self.player.play()
        self.print_current_info()

    def play_pause(self):
        if self.current_song is None:
            self._first_start()
        else:
            self.player.pause()

    def pause(self):
        if self.player.get_state() == vlc.State.Playing:
            self.player.pause()

    def play(self):
        if self.current_song is None:
            self._first_start()
        else:
            self.player.play()

    def skip(self):
        self.player.set_position(1.)

    def _add_to_history(self, song):
        if len(self.history) == self.max_history_size:
            self.history.pop()
        self.history.insert(0, song)

    def print_current_info(self):
        title = self.current_media.get_meta(vlc.Meta.Title)
        # length = self.player.get_length()/1000
        # length_string = f"({length//60}:{length%60})"
        print("")
        print("Now playing: ", title)
        print(self.current_song.file_name)
        print("Attributes:")
        print(self.storage.attribute_names)
        print("Current:")
        print(self.current_song.attributes)
        print("Target:")
        print(list(self.storage.target))
        print("Strength:")
        print(list(self.storage.strength))
        # print("")


class CommandLine:
    def __init__(self):
        self.player = MusicPlayer()
        self._start()

    def _start(self):
        answer = input("Use default library? [default, load, new] ")
        if answer == '' or answer == "default":
            self.player.load_storage()
            self.player.storage.update()
            print("default storage loaded")
        elif answer == 'load':
            filename = input("Filename: ")
            self.player.load_storage(filename)
            self.player.storage.update()
            print("Storage loaded")
        elif answer == 'new':
            self.player.generate_storage()
            print("New storage created!\nUse \"library <filename>\" to add a library")
        else:
            raise RuntimeError("Command not recognised")

    def main_loop(self):
        while True:
            command = input("")
            inputs = command.split()
            if inputs:
                first = inputs[0]
            else:
                continue
            if first == "help" or first == "h":
                print("Possible commands:")
                print("exit/quit/q")
                print("pause")
                print("play")
                print("p (pause/play)")
                print("skip")
                print("library <path to library>")
                print("save")
                print("add <attribute_name>")
                print("delete/remove <attribute_name/index>")
                print("set/change current/previous/target/strength")
                print("status/s")
                print("rename <attribute_name/index> <new_name>")
                print("move <attribute_name/index> <new_index>")
                print("history")
                print("refresh")

            elif first == "pause":
                # print("> pause")
                self.player.pause()
            elif first == "play":
                # print("> play")
                self.player.play()
            elif first == "p":
                self.player.play_pause()
            elif first == "skip":
                # print("> skip")
                self.player.skip()
            elif first == "library":
                if len(inputs) == 1:
                    print("Not enough inputs")
                    pass
                else:
                    path = ' '.join(inputs[1:])
                    try:
                        self.player.storage.import_library(path)
                    except FileNotFoundError:
                        print(f"File {path} not found")
            elif first == "save":
                self.player.storage.save()
            elif first == "add":
                if len(inputs) == 1:
                    print("Not enough inputs")
                    pass
                else:
                    self.player.storage.add_attribute(inputs[1])
                print(self.player.storage.attribute_names)
            elif first == "delete" or first == "remove":
                if len(inputs) == 1:
                    print("Not enough inputs")
                    pass
                else:
                    try:
                        self.player.storage.remove_attribute(inputs[1])
                    except ValueError:
                        print(f"Attribute not found")
                    except IndexError:
                        print(f"Index {inputs[1]} out of bounds")
                print(self.player.storage.attribute_names)
            elif first == "set" or first == "change":
                if inputs[1] == "current" or inputs[1] == "c":
                    song = self.player.current_song
                    print("Setting attributes for", song.file_name)
                    print("0: unset, 1: low, 2: moderate, 3: high")
                    print(self.player.storage.attribute_names)
                    print("Current attributes:", song.attributes)
                    new_string = input("New attributes:\n")
                    try:
                        attributes = [int(x) for x in new_string.split()]
                        self.player.change_attributes(attributes, song)
                    except ValueError:
                        print("Incorrect number of attributes or attribute outside of allowed range")
                elif inputs[1] == "previous" or inputs[1] == "p":
                    if len(self.player.history) <= 1:
                        print("No previous songs")
                    song = self.player.history[-2]
                    print("Setting attributes for ", song.file_name)
                    print("0: unset, 1: low, 2: moderate, 3: high")
                    print(self.player.storage.attribute_names)
                    print("Current attributes:", song.attributes)
                    new_string = input("New attributes:\n")
                    try:
                        attributes = [int(x) for x in new_string.split()]
                        self.player.change_attributes(attributes, song)
                    except ValueError:
                        print("Incorrect number of attributes or attribute outside of allowed range")
                elif inputs[1] == "target" or inputs[1] == "t":
                    print("0: unset, 1: low, 2: moderate, 3: high")
                    print("Current target:", self.player.storage.target)
                    new_string = input("New target:\n")
                    try:
                        target = np.array([int(x) for x in new_string.split()])
                        self.player.change_target(target, self.player.storage.strength)
                    except ValueError:
                        print("Incorrect number of attributes or attribute outside of allowed range")
                elif inputs[1] == "strength" or inputs[1] == "s":
                    print("1: ignore, 2: close, 3: perfect")
                    print("Current strength:", self.player.storage.strength)
                    new_string = input("New strength:\n")
                    try:
                        strength = np.array([int(x) for x in new_string.split()])
                        self.player.change_target(self.player.storage.target, strength)
                    except ValueError:
                        print("Incorrect number of strengths or strength outside of allowed range")
            elif first == "exit" or first == "quit" or first == "q":
                self.player.pause()
                break
            elif first == "status" or first == 's':
                # if self.player.current_song is not None:
                #     print("Current:", self.player.current_song.file_name, self.player.current_media.get_mrl().split('/')[-1])
                # if self.player.next_song is not None:
                #     print("Next:", self.player.next_song.file_name, self.player.next_media.get_mrl().split('/')[-1])
                # if self.player.player.get_media() is not None:
                #     print("Current:", self.player.player.get_media().get_mrl().split('/')[-1])
                # print("Status:", self.player.player.get_state())
                self.player.print_current_info()
            elif first == "rename":
                if len(inputs) < 3:
                    print("Not enough inputs")
                    pass
                else:
                    try:
                        self.player.storage.rename_attribute(inputs[1], inputs[2])
                    except ValueError:
                        print("New name cannot be numeric, or old name is not found")
                    except IndexError:
                        print("Index out of range")
                print(self.player.storage.attribute_names)
            elif first == "move":
                if len(inputs) < 3:
                    print("Not enough inputs")
                    pass
                else:
                    try:
                        self.player.storage.move_attribute(inputs[1], inputs[2])
                    except IndexError:
                        print("Index out of range")
                    except ValueError:
                        print("Name not found or new_index not integer")
                print(self.player.storage.attribute_names)
            elif first == "history":
                for i in range(len(self.player.history)):
                    print(self.player.history[i].file_name)
            elif first == "refresh":
                self.player.storage.update()
            else:
                print("Command not recognised")
            # if first != "skip":
            #     print("")


class GUI:
    def __init__(self, root):
        self.player = MusicPlayer()
        root.title("Calernia")
        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.control_column = ttk.Frame(self.mainframe)
        self.control_column.grid(column=0, row=0, sticky='nwes')
        ttk.Label(self.control_column, text='doot').grid(column=0, row=0, sticky='nsew')

        self.attribute_frame = ttk.Frame(self.mainframe)
        self.attribute_frame.grid(column=1, row=0, sticky='nwes')

        current_spinbox, target_spinbox, strength_spinbox, name_label = self.attribute_column()

        # for child in self.mainframe.winfo_children():
            # child
            # child['anchor'] = tk.CENTER
            # child['justify'] = 'center'
            # print(type(child))
            # print(child.configure('padding'))

    def attribute_column(self, index=0):
        # current_attribute = tk.IntVar()
        # target_attribute = tk.IntVar()
        # strength = tk.IntVar()
        # name = tk.StringVar()

        column = ttk.Frame(self.attribute_frame)
        column['borderwidth'] = 2
        column.grid(column=index, row=0, sticky='nwes')

        current_spinbox = ttk.Spinbox(column, from_=0, to=3)
        target_spinbox = ttk.Spinbox(column, from_=0, to=3)
        strength_spinbox = ttk.Spinbox(column, from_=0, to=3)
        name_label = ttk.Label(column, text="unset_name")

        current_spinbox.grid(column=0, row=0, sticky='nesw')
        ttk.Separator(column, orient='horizontal').grid(column=0, row=1, sticky='ew')
        target_spinbox.grid(column=0, row=2, sticky='nesw')
        strength_spinbox.grid(column=0, row=3, sticky='nesw')
        name_label.grid(column=0, row=4, sticky='nesw')

        return current_spinbox, target_spinbox, strength_spinbox, name_label






if __name__ == '__main__':
    # doot = CommandLine()
    # doot.main_loop()

    root = tk.Tk()
    gooy = GUI(root)


    def print_hierarchy(w, depth=0):
        print(
            '  ' * depth + w.winfo_class() + ' w=' + str(w.winfo_width()) + ' h=' + str(w.winfo_height()) + ' x=' + str(
                w.winfo_x()) + ' y=' + str(w.winfo_y()))
        for i in w.winfo_children():
            print_hierarchy(i, depth + 1)


    print_hierarchy(root)
    root.mainloop()

    # /media/arnalljm/windows/Users/arnal/Music/Nintendo/Disc 1/




