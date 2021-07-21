from filetypes import Folder, Song
import pickle
from numpy import random
import numpy as np
# from pygame.mixer import music
# import playsound
import vlc
import time
import pickle
import warnings


class SongStorage:
    def __init__(self):
        self.library_directories = []
        self.song_list = []
        self.attribute_names = []
        self.target = np.zeros(0, int)
        self.strength = np.zeros(0, int)
        self.save_name = self.DEFAULT_SAVE
        # self.current_song = None
        # self.next_song = None
        pass

    DEFAULT_SAVE = "music_library.p"
    DEFAULT_TARGET = 0
    DEFAULT_STRENGTH = 1
    DEFAULT_ATTRIBUTE = 0

    def save(self):
        with open(self.save_name, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(location=DEFAULT_SAVE):
        with open(location, 'rb') as file:
            result = pickle.load(file)
        return result

    @property
    def probabilities(self):
        result = np.zeros(len(self.song_list))
        for i in range(len(self.song_list)):
            result[i] = self.song_list[i].probability
        result = result/sum(result)
        return result

    def import_library(self, directory_name):
        # TODO check for pre-existing directory
        temp = Folder(path=directory_name)
        self.song_list.extend(temp.songs)
        self.library_directories.append(temp)
        print(f"imported {len(temp.songs)} songs")

    def _update_library(self, folder):
        new_songs = folder.update()
        self._merge_song_list(new_songs)

    def update(self):
        for folder in self.library_directories:
            self._update_library(folder)
        for song in self.song_list:
            song.update_cost(self.target, self.strength)

    def _merge_song_list(self, new_songs):
        self.song_list.extend(new_songs)

    def add_attribute(self, name, default_value=DEFAULT_ATTRIBUTE):
        for directory in self.library_directories:
            directory.add_attribute(default_value)
        self.target = np.append(self.target, SongStorage.DEFAULT_TARGET)
        self.strength = np.append(self.strength, SongStorage.DEFAULT_STRENGTH)
        self.attribute_names.append(name)
        # self.save()

    def remove_attribute(self, attribute):
        try:
            index = int(attribute)
        except ValueError:
            index = self.attribute_names.index(attribute)
        for directory in self.library_directories:
            directory.remove_attribute(index)
        self.target = np.delete(self.target, index)
        self.strength = np.delete(self.strength, index)
        # self.save()

    def change_target(self, target, strength):
        # result = []
        if isinstance(target, np.ndarray) and isinstance(strength, np.ndarray):
            pass
        else:
            raise TypeError("target and strength must be numpy arrays")
        if len(target) != len(self.target) or len(strength) != len(self.strength):
            raise ValueError("target and strength must be of appropriate length")
        if any(target > Song.ATTRIBUTE_RANGE[1]) or any(target < Song.ATTRIBUTE_RANGE[0]):
            raise ValueError("target must be in expected range")
        if any(strength > 3) or any(strength < 1):
            raise ValueError("strength must be in expected range")
        self.target = target
        self.strength = strength
        for song in self.song_list:
            song.update_cost(target, strength)
        #     result.append(song.probability)
        # return result

    def select_song(self, n=1):
        try:
            return random.choice(self.song_list, size=n, p=self.probabilities, replace=False)
        except ValueError:
            length = sum(self.probabilities > 0)
            print(f"Only {length} songs with nonzero probability")
            return random.choice(self.song_list, size=length, p=self.probabilities, replace=False)

    def rename_attribute(self, original_name, new_name):
        try:
            int(new_name)
            raise ValueError("New name cannot be numeric")
        except ValueError:
            pass
        try:
            index = int(original_name)
        except ValueError:
            index = self.attribute_names.index(original_name)
        self.attribute_names[index] = new_name

    def move_attribute(self, name, new_index):
        try:
            index = int(name)
        except ValueError:
            index = self.attribute_names.index(name)
        new_index = int(new_index)
        for song in self.song_list:
            song.move_attribute(index, new_index)
        attribute_name = self.attribute_names.pop(index)
        self.attribute_names.insert(new_index, attribute_name)

    def set_attribute(self, song, value, index=None):
        song.set_attribute(value, index)
        song.update_cost(self.target, self.strength)

    # def create_media(self, song):
    #     return self.instance.media_new(song.path)

    # def temp_play(self):
    #     song = self.select_song()
    #     print(song.file_name)
    #     media = self.create_media(song)
    #     self.media_list.insert_media(media, 0)
    #     self.player.play()
    #     # print(self.player.get_state())
    #     time.sleep(4)
