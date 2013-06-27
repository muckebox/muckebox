from shelltranscoder import ShellTranscoder

class MP3Transcoder(ShellTranscoder):
    QUALITY_MAP = {
        ShellTranscoder.Quality.LOWEST:         128,
        ShellTranscoder.Quality.LOW:            160,
        ShellTranscoder.Quality.MEDIUM:         192,
        ShellTranscoder.Quality.HIGH:           256,
        ShellTranscoder.Quality.HIGHEST:        320
        }

    def __init__(self, path, queue, quality):
        ShellTranscoder.__init__(self, path, queue, quality)

    def get_suffix(self):
        return 'mp3'

    def get_mime_type(self):
        return 'audio/mpeg'

    def set_quality(self, quality):
        self.quality = self.QUALITY_MAP[quality]

    def get_command(self):
        return [ 'ffmpeg',
                 '-i', self.path,
                 '-ab', "%dk" % (self.quality),
                 '-v', 'quiet',
                 '-f', 'mp3',
                 '-' ]

