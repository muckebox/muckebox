from vorbisfile import VorbisFile
from mutagen.oggvorbis import OggVorbis

class OggFile(VorbisFile):
    def parse_file(self):
        return OggVorbis(self.path)
