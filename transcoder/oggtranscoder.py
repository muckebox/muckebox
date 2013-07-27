from shelltranscoder import ShellTranscoder

class OggTranscoder(ShellTranscoder):
    QUALITY_MAP = {
        ShellTranscoder.Quality.LOWEST:         1,
        ShellTranscoder.Quality.LOW:            3,
        ShellTranscoder.Quality.MEDIUM:         5,
        ShellTranscoder.Quality.HIGH:           8,
        ShellTranscoder.Quality.HIGHEST:        10
        }

    def __init__(self, input, output):
        ShellTranscoder.__init__(self, input, output)

    def get_suffix(self):
        return 'ogg'

    def get_mime_type(self):
        return 'audio/ogg'

    def set_quality(self, quality):
        self.quality = self.QUALITY_MAP[quality]

    def get_command(self):
        return [ 'ffmpeg',
                 '-i', self.path,
                 '-aq', str(self.quality),
                 '-v', 'quiet',
                 '-f', 'ogg',
                 '-acodec', 'libvorbis',
                 '-ar', str(self.get_output_sample_rate()),
                 '-sample_fmt', 's%d' % (self.get_output_bits_per_sample()),
                 '-' ]
