from player import MusicPlayer
import numpy as np
import tkinter as tk
from tkinter import ttk
import vlc
import time


class GUI:
    def __init__(self, root):
        self.player = MusicPlayer()
        self.player.load_storage()
        self.player.storage.update()
        self.player.gui = self
        self.root = root

        # self.current_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)
        # self.target_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)
        # self.strength_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)


        self.attribute_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)

        self.current_dou = np.empty(len(self.player.storage.attribute_names), tk.DoubleVar)
        self.target_dou = np.empty(len(self.player.storage.attribute_names), tk.DoubleVar)
        self.strength_dou = np.empty(len(self.player.storage.attribute_names), tk.DoubleVar)

        root.title("Calernia")
        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.rowconfigure(0, weight=1)
        # self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        # self.mainframe.columnconfigure(2, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.control_column = ttk.Frame(self.mainframe)
        self.control_column.grid(column=0, row=0, sticky='nwe')
        # self.control_column.columnconfigure(0, weight=0)
        # self.control_column.rowconfigure(0, weight=0)
        self.confirm_button = None
        self.previous_button = None

        self.attribute_frame = ttk.Frame(self.mainframe)
        self.attribute_frame.grid(column=1, row=0, sticky='nwes')
        # self.attribute_frame.columnconfigure(0, weight=1)
        # self.attribute_frame.rowconfigure(0, weight=1)

        self.utility_column = ttk.Frame(self.mainframe)
        self.utility_column.grid(column=2, row=0, sticky='nwe')
        # self.utility_column.columnconfigure(0, weight=0)
        # self.utility_column.rowconfigure(0, weight=0)

        self.song_title = tk.StringVar()
        self.song_title.set("")
        self.song_title_label = ttk.Label(self.mainframe, textvariable=self.song_title)
        self.song_title_label.grid(column=0, row=1, columnspan=2, sticky='nwes')
        # self.song_title_label.columnconfigure(0, weight=1)
        # self.song_title_label.rowconfigure(0, weight=1)

        self.volume_variable = tk.IntVar()
        self.volume_variable.set(self.player.storage.volume)

        # current_spinbox, target_spinbox, strength_spinbox, name_label = self.attribute_column()
        # current_spinbox2, target_spinbox2, strength_spinbox2, name_label2 = self.attribute_column(1)
        # print(type(current_spinbox.get()))
        self.init_attribute_grid()
        self.init_control_column()
        self.init_utility_column()

        self.init_events()

    def init_events(self):
        self.root.bind('<XF86AudioPlay>', self.play_pause)
        self.root.bind('<XF86AudioStop>', self.play_pause)
        self.root.bind('<XF86AudioNext>', self.skip)
        self.root.bind('<XF86AudioPrev>', self.previous)
        self.root.bind('<p>', self.play_pause)

    def update_track_name(self):
        self.song_title.set(self.player.current_media.get_meta(vlc.Meta.Title))
        # print("doot")

    def play_pause(self, *args):
        self.player.play_pause()

    def skip(self, *args):
        self.player.skip()

    def previous(self, *args):
        self.player.previous()

    def init_control_column(self):
        play = ttk.Button(self.control_column, text='Play/Pause', command=self.player.play_pause)
        play.grid(column=0, row=0, sticky='nwes')
        skip = ttk.Button(self.control_column, text='Skip', command=self.player.skip)
        skip.grid(column=0, row=1, sticky='nwes')
        self.previous_button = ttk.Button(self.control_column, text='Previous', command=self.player.previous)
        self.previous_button.grid(row=2, sticky='nswe')
        self.previous_button.state(['disabled'])
        volume = ttk.Scale(self.control_column, orient=tk.VERTICAL, length=100, from_=100, to=0, variable=self.volume_variable, command=self.update_volume)
        volume.grid(row=3, sticky='nwes')

    def init_utility_column(self):
        self.confirm_button = ttk.Button(self.utility_column, text='Confirm', command=self.update_all)
        self.confirm_button.grid(sticky='nwes')
        self.toggle_confirm_button()
        save = ttk.Button(self.utility_column, text='Save', command=self.player.storage.save)
        save.grid(row=1, sticky='nswe')

    def update_volume(self, _):
        self.player.storage.volume = self.volume_variable.get()
        self.player.player.audio_set_volume(self.volume_variable.get())
        # self.player.player.audio_set_volume(100)

    def when_track_changed(self):
        # self.player.current_media.parse()
        self.player.event_manager.event_attach(vlc.EventType.MediaParsedChanged, self.update_track_name)
        self.player.current_media.parse_with_options(vlc.MediaParseFlag.local,100)
        while not self.player.current_media.is_parsed():
            pass
        if self.player.current_media.get_parsed_status() == vlc.MediaParsedStatus.timeout:
            print("Warning: failed to load metadata before timeout")
        # print(self.player.current_media.get_parsed_status())
        self.update_track_name()
        for i in range(len(self.player.current_song.attributes)):
            self.current_dou[i].set(self.player.current_song.attributes[i])
        if len(self.player.history) > 1:
            self.previous_button.state(['!disabled'])
        else:
            self.previous_button.state(['disabled'])
        self.toggle_confirm_button()

    def init_attribute_grid(self):
        # column = ttk.Frame(self.attribute_frame)
        # column['borderwidth'] = 2
        # column.grid(column=0, row=0, sticky='nwes')
        ttk.Label(self.attribute_frame, text='Current').grid(column=0, row=0, sticky='w')
        ttk.Label(self.attribute_frame, text='Target').grid(column=0, row=1, sticky='w')
        ttk.Label(self.attribute_frame, text='Strength').grid(column=0, row=2, sticky='w')
        self.attribute_frame.rowconfigure(0, weight=1)
        self.attribute_frame.rowconfigure(1, weight=1)
        self.attribute_frame.rowconfigure(2, weight=1)
        # self.attribute_frame.rowconfigure(3, weight=1)
        # label_length = max([len(label.get()) for label in self.attribute_str])


        for i in range(len(self.current_dou)):
            self.attribute_frame.columnconfigure(i+1, weight=1)
            self.current_dou[i] = tk.DoubleVar()
            self.target_dou[i] = tk.DoubleVar()
            self.strength_dou[i] = tk.DoubleVar()
            self.attribute_str[i] = tk.StringVar()
            # self.attribute_str[i].set("doot")

            self.current_dou[i].set(0)
            self.target_dou[i].set(self.player.storage.target[i])
            self.strength_dou[i].set(self.player.storage.strength[i])
            self.attribute_str[i].set(self.player.storage.attribute_names[i])

            # column = ttk.Frame(self.attribute_frame)
            # column['borderwidth'] = 2
            # column.grid(column=i+1, row=0, sticky='nwes')

            current_slider = ttk.Scale(self.attribute_frame, orient=tk.VERTICAL, length=100, from_=3, to=0, variable=self.current_dou[i], command=self.round_all_doubles)
            target_slider = ttk.Scale(self.attribute_frame, orient=tk.VERTICAL, length=100, from_=3, to=0, variable=self.target_dou[i], command=self.round_all_doubles)
            strength_slider = ttk.Scale(self.attribute_frame, orient=tk.VERTICAL, length=100, from_=3, to=0, variable=self.strength_dou[i], command=self.round_all_doubles)
            name_label = ttk.Label(self.attribute_frame, textvariable=self.attribute_str[i])

            current_slider.grid(column=i+1, row=0, sticky='nesw', pady=5)
            # ttk.Separator(column, orient='horizontal').grid(column=0, row=1, sticky='ew')
            target_slider.grid(column=i+1, row=1, sticky='nesw', pady=5)
            strength_slider.grid(column=i+1, row=2, sticky='nesw', pady=5)
            name_label.grid(column=i+1, row=3, sticky='n')

    def round_all_doubles(self, *args):
        for i in range(len(self.current_dou)):
            self.current_dou[i].set(round(self.current_dou[i].get()))
            self.target_dou[i].set(round(self.target_dou[i].get()))
            self.strength_dou[i].set(round(self.strength_dou[i].get()))
        self.update_target_strength()
        self.toggle_confirm_button()

    def update_current(self):
        if self.player.current_song is None:
            return
        # print([thing.get() for thing in self.current_str])
        new_current = self.doublevar_to_int(self.current_dou).tolist()  # TODO modify to accept arrays
        self.player.change_attributes(new_current, self.player.current_song)
        # self.player.print_current_info()
        # print(new_current)

    def update_target_strength(self):
        new_strength = self.doublevar_to_int(self.strength_dou)
        new_target = self.doublevar_to_int(self.target_dou)
        self.player.change_target(new_target, new_strength)
        # self.player.print_current_info()

    def update_all(self):
        self.update_current()
        self.update_target_strength()
        self.toggle_confirm_button()
        self.player.print_current_info()

    @staticmethod
    def compare_attributes(a,b):
        if len(a) != len(b):
            raise RuntimeError("Attributes cannot be compared")
        for i in range(len(a)):
            if a[i] != b[i]:
                return False
        return True

    def toggle_confirm_button(self):
        if self.compare_attributes(self.player.storage.target, self.doublevar_to_int(self.target_dou)):
            if self.compare_attributes(self.player.storage.strength, self.doublevar_to_int(self.strength_dou)):
                if self.player.current_song is None:
                    self.confirm_button.state(['disabled'])
                    return
                if self.compare_attributes(self.player.current_song.attributes, self.doublevar_to_int(self.current_dou)):
                    self.confirm_button.state(['disabled'])
                    return
        self.confirm_button.state(['!disabled'])

    @staticmethod
    def stringvar_to_int(input):
        if type(input) == tk.StringVar:
            if input.get() == "":
                return -1
            return int(input.get())

        output = np.empty(len(input), int)
        for i in range(len(input)):
            if input[i].get() == "":
                output[i] = -1
            else:
                output[i] = int(input[i].get())
        return output

    @staticmethod
    def doublevar_to_int(input):
        if type(input) == tk.DoubleVar:
            return int(round(input.get()))

        output = np.empty(len(input), int)
        for i in range(len(input)):
            output[i] = int(round(input[i].get()))
        return output


# class CustomScale(ttk.Scale):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)








if __name__ == '__main__':
    # doot = CommandLine()
    # doot.main_loop()

    # print(vlc.__file__)
    root = tk.Tk()
    gooy = GUI(root)


    # def print_hierarchy(w, depth=0):
    #     print(
    #         '  ' * depth + w.winfo_class() + ' w=' + str(w.winfo_width()) + ' h=' + str(w.winfo_height()) + ' x=' + str(
    #             w.winfo_x()) + ' y=' + str(w.winfo_y()))
    #     for i in w.winfo_children():
    #         print_hierarchy(i, depth + 1)


    # print_hierarchy(root)
    # gooy.player.play()
    root.mainloop()

    # /media/arnalljm/windows/Users/arnal/Music/Nintendo/Disc 1/




