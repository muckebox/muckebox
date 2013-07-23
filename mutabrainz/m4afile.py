from audiofile import AudioFile

from mutagen.mp4 import MP4

class M4AFile(AudioFile):
    tag_map = {
        'artist':               '\xa9ART',
        'title':                '\xa9nam',
        'album':                '\xa9alb',
        'albumartist':          'aART',
        'date':                 '\xa9day',
        'tracknumber':          'trkn',
        'discnumber':           'disk',
        'label':                '----:com.apple.iTunes:LABEL',
        'catalognumber':        '----:com.apple.iTunes:CATALOGNUMBER'
        }

    tuple_tags = ( 'trkn', 'disk' )

    def parse_file(self):
        return MP4(self.path)
    
    def get_tracks(self):
        tags = { }
        file = self.get_file()

        for mp4_key in self.tag_map.values():
            if mp4_key in file:
                tags[mp4_key] = file[mp4_key]

                if mp4_key in self.tuple_tags:
                    tags[mp4_key] = tags[mp4_key][0][0]
                
        return [ self.make_track(self.path, tags, self.tag_map) ]
