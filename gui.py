from player import MusicPlayer
import numpy as np
import tkinter as tk
from tkinter import ttk
import vlc


class GUI:
    def __init__(self, root):
        self.player = MusicPlayer()
        self.player.load_storage()
        self.player.storage.update()
        self.player.gui = self

        self.current_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)
        self.target_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)
        self.strength_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)
        self.attribute_str = np.empty(len(self.player.storage.attribute_names), tk.StringVar)

        root.title("Calernia")
        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.control_column = ttk.Frame(self.mainframe)
        self.control_column.grid(column=0, row=0, sticky='nwes')
        self.confirm_button = None

        self.attribute_frame = ttk.Frame(self.mainframe)
        self.attribute_frame.grid(column=1, row=0, sticky='nwes')

        self.utility_column = ttk.Frame(self.mainframe)
        self.utility_column.grid(column=2, row=0, sticky='nwes')

        self.song_title = tk.StringVar()
        self.song_title.set("")
        self.song_title_label = ttk.Label(self.mainframe, textvariable=self.song_title)
        self.song_title_label.grid(column=0, row=1, columnspan=2, sticky='nwes')

        # current_spinbox, target_spinbox, strength_spinbox, name_label = self.attribute_column()
        # current_spinbox2, target_spinbox2, strength_spinbox2, name_label2 = self.attribute_column(1)
        # print(type(current_spinbox.get()))
        self.init_attribute_grid()
        self.init_control_column()
        self.init_utility_column()

    def init_control_column(self):
        play = ttk.Button(self.control_column, text='Play/Pause', command=self.player.play_pause)
        play.grid(column=0, row=0, sticky='nwes')
        skip = ttk.Button(self.control_column, text='Skip', command=self.player.skip)
        skip.grid(column=0, row=1, sticky='nwes')

    def init_utility_column(self):
        self.confirm_button = ttk.Button(self.utility_column, text='Confirm', command=self.update_all)
        self.confirm_button.grid(sticky='nwes')
        self.toggle_confirm_button()
        save = ttk.Button(self.utility_column, text='Save', command=self.player.storage.save)
        save.grid(row=1, sticky='nswe')

    def when_track_changed(self):
        self.song_title.set(self.player.current_media.get_meta(vlc.Meta.Title))
        for i in range(len(self.player.current_song.attributes)):
            self.current_str[i].set(str(self.player.current_song.attributes[i]))

    def init_attribute_grid(self):
        column = ttk.Frame(self.attribute_frame)
        column['borderwidth'] = 2
        column.grid(column=0, row=0, sticky='nwes')
        ttk.Label(column, text='Current').grid(column=0, row=0, sticky='nsew')
        ttk.Label(column, text='Target').grid(column=0, row=1, sticky='nsew')
        ttk.Label(column, text='Strength').grid(column=0, row=2, sticky='nsew')

        for i in range(len(self.current_str)):
            self.current_str[i] = tk.StringVar()
            self.target_str[i] = tk.StringVar()
            self.strength_str[i] = tk.StringVar()
            self.attribute_str[i] = tk.StringVar()
            # self.attribute_str[i].set("doot")

            self.current_str[i].set('0')
            self.target_str[i].set(str(self.player.storage.target[i]))
            self.strength_str[i].set(str(self.player.storage.strength[i]))
            self.attribute_str[i].set(str(self.player.storage.attribute_names[i]))

            column = ttk.Frame(self.attribute_frame)
            column['borderwidth'] = 2
            column.grid(column=i+1, row=0, sticky='nwes')

            current_spinbox = ttk.Spinbox(column, from_=0, to=3, textvariable=self.current_str[i], command=self.toggle_confirm_button)
            target_spinbox = ttk.Spinbox(column, from_=0, to=3, textvariable=self.target_str[i], command=self.toggle_confirm_button)
            strength_spinbox = ttk.Spinbox(column, from_=0, to=3, textvariable=self.strength_str[i], command=self.toggle_confirm_button)
            name_label = ttk.Label(column, textvariable=self.attribute_str[i])

            current_spinbox.grid(column=0, row=0, sticky='nesw')
            # ttk.Separator(column, orient='horizontal').grid(column=0, row=1, sticky='ew')
            target_spinbox.grid(column=0, row=1, sticky='nesw')
            strength_spinbox.grid(column=0, row=2, sticky='nesw')
            name_label.grid(column=0, row=3, sticky='nesw')

    def update_current(self):
        if self.player.current_song is None:
            return
        # print([thing.get() for thing in self.current_str])
        new_current = self.stringvar_to_int(self.current_str).tolist()  # TODO modify to accept arrays
        self.player.change_attributes(new_current, self.player.current_song)
        self.player.print_current_info()
        # print(new_current)

    def update_target_strength(self):
        new_strength = self.stringvar_to_int(self.strength_str)
        new_target = self.stringvar_to_int(self.target_str)
        self.player.change_target(new_target, new_strength)
        self.player.print_current_info()

    def update_all(self):
        self.update_current()
        self.update_target_strength()
        self.toggle_confirm_button()

    @staticmethod
    def compare_attributes(a,b):
        if len(a) != len(b):
            raise RuntimeError("Attributes cannot be compared")
        for i in range(len(a)):
            if a[i] != b[i]:
                return False
        return True

    def toggle_confirm_button(self):
        if self.compare_attributes(self.player.storage.target, self.stringvar_to_int(self.target_str)):
            if self.compare_attributes(self.player.storage.strength, self.stringvar_to_int(self.strength_str)):
                if self.player.current_song is None:
                    self.confirm_button.state(['disabled'])
                    return
                if self.compare_attributes(self.player.current_song.attributes, self.stringvar_to_int(self.current_str)):
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
    # gooy.player.play()
    root.mainloop()

    # /media/arnalljm/windows/Users/arnal/Music/Nintendo/Disc 1/




