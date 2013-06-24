from audiofile import AudioFile

from mp3file import MP3File
from oggfile import OggFile
from flacfile import FLACFile

class AutoFile(AudioFile):
    extension_map = {
        'mp3': MP3File,
        'ogg': OggFile,
        'flac': FLACFile
    }

    def __init__(self, path):
        AudioFile.__init__(self, path)
                
        self.instance = (self.extension_to_class(self.path))(self.path)

    @classmethod
    def get_extension(cls, filename):
        return filename[filename.rfind('.') + 1:].lower()

    @classmethod
    def extension_to_class(cls, filename):
        return cls.extension_map[cls.get_extension(filename)]

    @classmethod
    def is_supported(cls, filename):
        return cls.get_extension(filename) in cls.extension_map

    def parse_file(self):
        return self.instance.parse_file()

    def get_tracks(self):
        return self.instance.get_tracks()
        
        
