from vorbisfile import VorbisFile
from mutagen.flac import FLAC

class FLACFile(VorbisFile):
    def parse_file(self):
        return FLAC(self.path)

    def get_picture(self):
        if len(self.get_file().pictures) > 0:
            pic = self.get_file().pictures[0]
            return (pic.mime, pic.data)

        return VorbisFile.get_picture(self)
        
