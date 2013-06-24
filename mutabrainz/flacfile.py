from vorbisfile import VorbisFile
from mutagen.flac import FLAC

class FLACFile(VorbisFile):
    def parse_file(self):
        return FLAC(self.path)
        
