import os.path

from abc import ABCMeta, abstractmethod
from types import ListType

from artwork import Artwork
from numberparser import NumberParser

class AudioFile:
    __metaclass__ = ABCMeta

    def __init__(self, path):
        self.path = path
        self.file = False
        
    @abstractmethod
    def parse_file(self):
        return False

    @abstractmethod
    def get_tracks(self):
        return False

    def get_picture(self):
        ret = Artwork.get_cover(self.get_path())

        if ret:
            return ret

        return False

    def get_path(self):
        return self.path

    def get_file(self):
        if not self.file:
            self.file = self.parse_file()

        return self.file

    def make_track(self, string_id, tags, mapping):
        track = { }

        track['stringid'] = string_id
        track['directory'] = os.path.dirname(string_id)
        track['length'] = int(self.get_length())
        track['bits_per_sample'] = int(self.get_bits_per_sample())
        track['sample_rate'] = int(self.get_sample_rate())

        for k in mapping.keys():
            if mapping[k] in tags:
                track[k] = tags[mapping[k]]

                if isinstance(track[k], ListType):
                    track[k] = track[k][0]

        track['title'] = track.get('title') or \
            os.path.splitext(os.path.basename(string_id))[0]
        track['album'] = track.get('album') or \
            os.path.basename(track['directory'])
        (track['tracknumber'], track['discnumber']) = \
            NumberParser.parse(track.get('tracknumber', 1), \
                                   track.get('discnumber', 1))

        return track

    def get_mtime(self):
        return os.path.getmtime(self.path)

    def get_length(self):
        return self.get_file().info.length

    def get_bits_per_sample(self):
        info = self.get_file().info
        
        if hasattr(info, 'bits_per_sample'):
            return info.bits_per_sample

        return 16

    def get_sample_rate(self):
        return self.get_file().info.sample_rate

