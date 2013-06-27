from shelltranscoder import ShellTranscoder

class MP3Transcoder(ShellTranscoder):
    QUALITY_MAP = {
        ShellTranscoder.Quality.LOWEST:         128,
        ShellTranscoder.Quality.LOW:            160,
        ShellTranscoder.Quality.MEDIUM:         192,
        ShellTranscoder.Quality.HIGH:           256,
        ShellTranscoder.Quality.HIGHEST:        320
        }

    def __init__(self, path, queue):
        ShellTranscoder.__init__(self, path, queue)

        self.quality = 256

    def get_suffix(self):
        return 'mp3'

    def get_mime_type(self):
        return 'audio/mpeg'

    def set_quality(self, quality):
        self.quality = QUALITY_MAP[quality]

    def get_command(self):
        return [ 'ffmpeg',
                 '-i', self.path,
                 '-ab', str(self.quality),
                 '-v', 'quiet',
                 '-f', 'ogg',
                 '-' ]

