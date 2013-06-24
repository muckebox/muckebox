from audiofile import AudioFile

class VorbisFile(AudioFile):
    tag_map = {
        'artist':               'ARTIST',
        'title':                'TITLE',
        'album':                'ALBUM',
        'albumartist':          'ALBUMARTIST',
        'date':                 'DATE',
        'tracknumber':          'TRACKNUMBER',
        'discnumber':           'DISCNUMBER',
        'label':                'LABEL',
        'catalognumber':        'CATALOGNUMBER'
        }
    
    def get_tracks(self):
        return [ self.make_track(self.path, self.get_file(), self.tag_map) ]
