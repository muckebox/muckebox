from audiofile import AudioFile
from mutagen.mp3 import MP3
from mutagen.id3 import NumericTextFrame, NumericPartTextFrame

class MP3File(AudioFile):
    tag_map = {
        'artist':               'TPE1',
        'title':                'TIT2',
        'album':                'TALB',
        'albumartist':          'TPE2',
        # 'date':                 'TDRC',
        'tracknumber':          'TRCK',
        'discnumber':           'TPOS',
        'label':                'TPUB',
        'catalognumber':        'TXXX:CATALOGNUMBER'
        }

    def parse_file(self):
        return MP3(self.path)

    def get_tracks(self):
        tags = { }
        file = self.get_file()

        for tag in self.tag_map.values():
            if tag in file:
                if isinstance(file[tag], NumericTextFrame) or \
                        isinstance(file[tag], NumericPartTextFrame):
                    tags[tag] = + file[tag]
                else:
                    tags[tag] = file[tag].text

        return [ self.make_track(self.path, tags, self.tag_map) ]

