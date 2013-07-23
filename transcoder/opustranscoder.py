import subprocess

from shelltranscoder import ShellTranscoder

class OpusTranscoder(ShellTranscoder):
    QUALITY_MAP = {
        ShellTranscoder.Quality.LOWEST:         96,
        ShellTranscoder.Quality.LOW:            112,
        ShellTranscoder.Quality.MEDIUM:         128,
        ShellTranscoder.Quality.HIGH:           160,
        ShellTranscoder.Quality.HIGHEST:        192
        }

    def __init__(self, path, queue, quality):
        ShellTranscoder.__init__(self, path, queue, quality)

    def get_suffix(self):
        return 'opus'

    def get_mime_type(self):
        return 'audio/ogg'

    def set_quality(self, quality):
        self.quality = self.QUALITY_MAP[quality]

    def start_process(self):
        self.decode_process = subprocess.Popen(
            [ 'ffmpeg', '-i', self.path,
              '-v', 'quiet',
              '-f', 'wav',
              '-ar', str(self.get_output_sample_rate()),
              '-sample_fmt', 's%d' % (self.get_output_bits_per_sample()),
              '-', ], stdout = subprocess.PIPE,
            bufsize = self.BLOCK_SIZE)
        self.process = subprocess.Popen(
            [ 'opusenc',
              '--quiet',
              '--music',
              '--bitrate', str(self.quality),
              '-',
              '-' ],
            stdin = self.decode_process.stdout,
            stdout = subprocess.PIPE,
            bufsize = self.BLOCK_SIZE)

    def stop_process(self):
        if self.decode_process:
            self.decode_process.kill()

        ShellTranscoder.stop_process(self)

    def get_command(self):
        return False
