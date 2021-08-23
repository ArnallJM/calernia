import os
import warnings
# from pygame.mixer import music
# from pygame import event
import song

try:
    from tinytag import TinyTag
    tiny_import = True
except ModuleNotFoundError:
    warnings.warn("TinyTag not installed - metadata unavailable")
    tiny_import = False


class File:
    """Class for keeping track of files"""
    def __init__(self, parent=None, file_name=None, path=None):
        if path is not None:
            if not isinstance(path, str):
                raise TypeError("path must be a string")
            self._parent = None
            self.file_name = path
        else:
            if not isinstance(parent, Folder):
                raise TypeError("parent must be a Folder")
            if not isinstance(file_name, str):
                raise TypeError("file_name must be a string")
            self._parent = parent
            self.file_name = file_name
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"{path} not found")

    @property
    def path(self):
        if self._parent:
            full_path = os.path.join(self._parent.path, self.file_name)
        else:
            full_path = self.file_name
        return full_path


class Song(File):
    """Everything to know about a song except for the music itself"""
    def __init__(self, parent=None, file_name=None, path=None, attribute_count=0):
        super().__init__(parent=parent, file_name=file_name, path=path)
        # self.tags = TinyTag.get(path)
        self.attributes = []
        for i in range(attribute_count):
            self.attributes.append(song.SongStorage.DEFAULT_ATTRIBUTE)
        # self.play_count = 0
        self.cost = 0
        pass

    allowed_filetypes = (
        # # "wav",
        "mp3",
        # # "flac",
        "m4a",
        # # "mp4",
        # # "m4b",
        "wma"
    )
    # play_count_scalar = 10
    skipped_filetypes = {}
    ATTRIBUTE_RANGE = (0, 3)
    MATCH_SCALE = 3
    HARD_MATCH_SCALE = 7

    # def _probability_fn(self, weights):
    #     probability = 1  # to do? decide whether I want a default nonzero probability
    #     for i in range(len(self.attributes)):
    #         if self.attributes[i] == -1:
    #             continue
    #         else:
    #             probability += self.attributes[i] * weights[i]
    #     probability /= self.play_count_scalar**(-self.play_count)
    #     return probability

    @property
    def tags(self, image=False):
        if tiny_import:
            return TinyTag.get(self.path, image=image)
        else:
            return None

    @property
    def probability(self):
        if self.cost == -1:
            return 0
        return 1/(1+self.cost)

    # def probability(self, weights, include=None):
    #     if include is None:
    #         include = [0]*len(self.attributes)
    #     elif len(include) != len(self.attributes):
    #         raise ValueError("Include must be same length as Attributes")
    #     if len(weights) != len(self.attributes):
    #         raise ValueError("Weights must be same length as Attributes")
    #
    #     for i in range(len(self.attributes)):
    #         if include[i] == 1 & self.attributes[i] == 0:
    #             return 0
    #         if include[i] == -1 & self.attributes[i] != 0:
    #             return 0
    #
    #     return self._probability_fn(weights)

    def update_cost(self, target, strength):
        if len(target) != len(self.attributes):
            raise ValueError("Target must be same length as Attributes")
        if len(strength) != len(self.attributes):
            raise ValueError("Strength must be same length as Attributes")
        cost = 0
        for i in range(len(self.attributes)):
            if target[i] == 0 and strength[i] != 0:
                # Want unset attribute
                if self.attributes[i] == 0:
                    continue
                else:
                    self.cost = -1
                    return self.cost
            if self.attributes[i] == 0:
                if target[i] != 0:
                    # Attribute unset
                    self.cost = -1
                    return self.cost
                else:
                    # Attribute unset but no-one cares
                    pass
            if strength[i] == 0:
                # No impact
                pass
            elif strength[i] == 1:
                # close match
                cost += self.MATCH_SCALE*(self.attributes[i]-target[i])**4
            elif strength[i] == 2:
                # very close match
                diff = abs(self.attributes[i]-target[i])
                if diff > 1:
                    self.cost = -1
                    return self.cost
                cost += self.HARD_MATCH_SCALE*diff
            elif strength[i] == 3:
                # exact match
                if self.attributes[i] != target[i]:
                    self.cost = -1
                    return self.cost
        self.cost = cost
        return self.cost

    def remove_attribute(self, index):
        if index >= len(self.attributes):
            raise IndexError(f"Index {index} out of bounds of range {len(self.attributes)}")
        self.attributes.pop(index)

    def add_attribute(self, value=0):
        self.attributes.append(0)
        if value != 0:
            self.set_attribute(value, index=-1)

    def set_attribute(self, value, index=None):
        if index is None and not isinstance(value, list):
            raise ValueError("Specify an index or give a list of values to set")
        if isinstance(value, list):
            if len(value) != len(self.attributes):
                raise ValueError(
                    f"Number of values ({len(value)}) does not match number of attributes ({len(self.attributes)})")
        if index is not None and isinstance(value, list):
            warnings.warn("Index ignored as a list of values was given")

        if isinstance(value, list):
            for i in range(len(self.attributes)):
                if value[i] < self.ATTRIBUTE_RANGE[0] or value[i] > self.ATTRIBUTE_RANGE[1]:
                    raise ValueError("New value of attribute is out of the expected range")
            for i in range(len(self.attributes)):
                self.attributes[i] = value[i]
        else:
            if value < self.ATTRIBUTE_RANGE[0] or value > self.ATTRIBUTE_RANGE[1]:
                raise ValueError("New value of attribute is out of the expected range")
            self.attributes[index] = value

    def move_attribute(self, current_index, new_index):
        self.attributes[new_index]
        attribute = self.attributes.pop(current_index)
        self.attributes.insert(new_index, attribute)


class Folder(File):
    def __init__(self, parent=None, file_name=None, path=None, attribute_count=0):
        super().__init__(parent=parent, file_name=file_name, path=path)
        self._songs = []
        self._directories = []
        self.attribute_count = attribute_count
        self._build()

    def _add_file(self, file_name):
        """Also returns any new songs as a list"""
        if os.path.isdir(os.path.join(self.path, file_name)):
            temp = Folder(parent=self, file_name=file_name, attribute_count=self.attribute_count)
            self._directories.append(temp)
            return temp.songs
        else:
            if file_name[0] == '.':
                return []
            extension = file_name.split('.')[-1]
            if extension.lower() in Song.allowed_filetypes:
                temp = Song(parent=self, file_name=file_name, attribute_count=self.attribute_count)
                self._songs.append(temp)
                return [temp]
            elif extension.lower() not in Song.skipped_filetypes.keys():
                Song.skipped_filetypes[extension] = 1
            else:
                Song.skipped_filetypes[extension] += 1
            return []

    def _build(self):
        for file in os.listdir(self.path):
            self._add_file(file)

    def update(self):
        """Checks for new folders and songs, and returns a list of new song objects"""
        current_folders = [file.file_name for file in self._directories]
        current_songs = [file.file_name for file in self._songs]
        new_songs = []
        for file in os.listdir(self.path):
            if file in current_folders:
                continue
            if file in current_songs:
                continue
            new_songs.extend(self._add_file(file))
        for directory in self._directories:
            new_songs.extend(directory.update())
        return new_songs

    @property
    def songs(self):
        result = []
        result.extend(self._songs)
        for directory in self._directories:
            result.extend(directory.songs)
        return result

    def remove_attribute(self, index):
        if index >= self.attribute_count:
            raise IndexError(f"Index {index} out of bounds of range {self.attribute_count}")
        for file in self._directories:
            file.remove_attribute(index)
        for file in self._songs:
            file.remove_attribute(index)
        self.attribute_count -= 1

    def add_attribute(self, default_value=0):
        for file in self._directories:
            file.add_attribute(default_value)
        for file in self._songs:
            file.add_attribute(default_value)
        self.attribute_count += 1

    def set_folder_attribute(self, value, index=None):
        for file in self._directories:
            file.set_folder_attribute(value, index)
        for file in self._songs:
            file.set_attribute(value, index)
