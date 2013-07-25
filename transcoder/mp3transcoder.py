from shelltranscoder import ShellTranscoder

class MP3Transcoder(ShellTranscoder):
    QUALITY_MAP = {
        ShellTranscoder.Quality.LOWEST:         128,
        ShellTranscoder.Quality.LOW:            160,
        ShellTranscoder.Quality.MEDIUM:         192,
        ShellTranscoder.Quality.HIGH:           256,
        ShellTranscoder.Quality.HIGHEST:        320
        }

    def __init__(self, input, queue, output):
        ShellTranscoder.__init__(self, input, queue, output)

    def get_suffix(self):
        return 'mp3'

    def get_mime_type(self):
        return 'audio/mpeg'

    def set_quality(self, quality):
        self.quality = self.QUALITY_MAP[quality]

    def get_command(self):
        return [ 'ffmpeg',
                 '-i', self.path,
                 '-ab', '%dk' % (self.quality),
                 '-ar', str(self.get_output_sample_rate()),
                 '-sample_fmt', 's%d' % (self.get_output_bits_per_sample()),
                 '-v', 'quiet',
                 '-f', 'mp3',
                 '-' ]

